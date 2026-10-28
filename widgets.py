from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt, QRectF, QTimer, QSize
from PyQt5.QtGui import QPainter, QFont, QColor, QPixmap
from logic import resource_path
import os

class NavisionTitle(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.word = "NAVISION"
        self.letter_width = 32 # every letter gets its own fixed-width "cell"

        self.title_font = QFont("Consolas", 22)
        self.title_font.setBold(True)

        self.setMinimumHeight(50)

        # Animation settings
        self.max_zoom = 0.6 # the letters under the lens grows to 1.6x its size
        self.lens_speed = 0.08 # how many letters the lens moves per tick
        self.lens_pos = -1.0 # start just left of the first letter

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_lens)
        self.timer.start(30) # ticke every 30 ms (~33 frames per second)

    def move_lens(self):
        self.lens_pos += self.lens_speed

        # Past the last letter (plus a small pause) - jump back to the start
        if self.lens_pos > len(self.word) + 1:
            self.lens_pos = -1.0

        self.update() # ask Qt to call paintEvent again

    def letter_scale(self, index):
        # 0 = lens right on the letter, 1 or more = lens is a full letter away
        distance = abs(index - self.lens_pos)
        strength = max(0.0, 1.0 - distance)
        return 1.0 + self.max_zoom * strength

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setFont(self.title_font)
        painter.setPen(QColor("#333333"))

        # Center the word horizontally
        total_width = self.letter_width * len(self.word)
        x = (self.width() - total_width) / 2
        center_y = self.height() / 2

        for index in range(len(self.word)):
            letter = self.word[index]
            scale = self.letter_scale(index)
            center_x = x + self.letter_width / 2

            painter.save()
            painter.translate(center_x, center_y) # move the origin to the letter's center
            painter.scale(scale, scale) # zoom around that center
            cell = QRectF(-self.letter_width / 2, -self.height() / 2, self.letter_width, self.height())
            painter.drawText(cell, Qt.AlignCenter, letter)
            painter.restore() # undo translate + scale for the next letter

            x += self.letter_width

        painter.end()

class TopBar(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setObjectName("TopBar")
        self.setFixedHeight(70)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            #TopBar{
                background-color: #e3e3e3;
                border-bottom: 1px solid #a6aba7;
            }
    """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        self.setLayout(layout)

        self.title = NavisionTitle()

        self.btn_expand = QPushButton(">>")
        self.btn_expand.setFixedSize(40, 40)
        self.btn_expand.setToolTip("Expand window")

        layout.addSpacing(40) # same width as btn_expand, keeps the title truly centered.
        layout.addWidget(self.title, 1)
        layout.addWidget(self.btn_expand)

class SideBar(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedWidth(100)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        self.setLayout(layout)

        self.btn_filter_1 = QPushButton("|*")
        self.btn_filter_2 = QPushButton("|")
        self.btn_filter_3 = QPushButton("&&<>")
        self.btn_remdupes = QPushButton("rem dupes")
        self.btn_screenshot = QPushButton("OCR")
        self.btn_clear = QPushButton("Clear")

        # Hover hints
        self.btn_filter_1.setToolTip("Filter by |*")
        self.btn_filter_2.setToolTip("Filter by |")
        self.btn_filter_3.setToolTip("Filter by &<>")
        self.btn_remdupes.setToolTip("Remove duplicate values")
        self.btn_screenshot.setToolTip("Screenshot -> Text")
        self.btn_clear.setToolTip("Clear the text")

        layout.addWidget(self.btn_filter_1)
        layout.addWidget(self.btn_filter_2)
        layout.addWidget(self.btn_filter_3)
        layout.addWidget(self.btn_remdupes)
        layout.addWidget(self.btn_screenshot)
        layout.addStretch()
        layout.addWidget(self.btn_clear)

class PlainTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setPlaceholderText("Paste your text here ^-^")

        text_font = QFont("Cascadia Code")
        text_font.setPixelSize(15)
        self.setFont(text_font)

        # Background image
        self.bg_original = QPixmap(resource_path(os.path.join("icons", "KatoenNatie.png")))
        self.bg_scaled = None
        self.bg_scaled_for = None # the size the cached copy was made for

    def insertFromMimeData(self, source):
        # Paste as plain text only (no formatting from Excel, web pages, etc.)
        if source.hasText():
            self.insertPlainText(source.text())
        else:
            super().insertFromMimeData(source)

    def scaled_background(self):
        # Real pixels = size on screen * monitor scaling (1.0, 1.25, 1.50...)
        ratio = self.viewport().devicePixelRatioF()
        target = QSize(int(self.viewport().width() * ratio), int(self.viewport().height() * ratio))

        # Only rescale when the size or monitor scaling changed - not on every keystroke
        if self.bg_scaled_for != target:
            self.bg_scaled = self.bg_original.scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.bg_scaled.setDevicePixelRatio(ratio)
            self.bg_scaled_for = target

        return self.bg_scaled

    def paintEvent(self, event):
        if not self.bg_original.isNull():
            pixmap = self.scaled_background()

            # Size of the picture on screen
            ratio = pixmap.devicePixelRatio()
            img_w = pixmap.width() / ratio
            img_h = pixmap.height() / ratio
            x = int((self.viewport().width() - img_w) / 2)
            y = int((self.viewport().height() - img_h) / 2)

            painter = QPainter(self.viewport())
            painter.drawPixmap(x, y, pixmap)
            painter.end()

        # Let QtextEdit draw the text on top
        super().paintEvent(event)


