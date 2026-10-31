from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, 
                             QLineEdit, QGridLayout)
from PyQt5.QtCore import Qt, QRectF, QTimer, QSize, QEvent
from PyQt5.QtGui import QPainter, QFont, QColor, QPixmap, QIcon, QTextCursor
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

        self.btn_expand = QPushButton()
        self.btn_expand.setIcon(QIcon(resource_path(os.path.join("icons", "expand.png"))))
        self.btn_expand.setIconSize(QSize(30, 30))
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
        self.btn_screenshot = QPushButton()
        self.btn_screenshot.setIcon(QIcon(resource_path(os.path.join("icons", "image.png"))))
        self.btn_screenshot.setIconSize(QSize(30, 30))
        self.btn_clear = QPushButton()
        self.btn_clear.setIcon(QIcon(resource_path(os.path.join("icons", "broom.png"))))
        self.btn_clear.setIconSize(QSize(30, 30))

        # Hover hints
        self.btn_filter_1.setToolTip("Filter by |*")
        self.btn_filter_2.setToolTip("Filter by |")
        self.btn_filter_3.setToolTip("Filter by &<>")
        self.btn_remdupes.setToolTip("Remove duplicate values")
        self.btn_screenshot.setToolTip("Screenshot -> Text")
        self.btn_clear.setToolTip("Clear the text")

        # Clicking a side bar button must not steal focus from the text area,
        # otherwise Ctrl+Z would go to the button instead of the text
        self.btn_filter_1.setFocusPolicy(Qt.NoFocus)
        self.btn_filter_2.setFocusPolicy(Qt.NoFocus)
        self.btn_filter_3.setFocusPolicy(Qt.NoFocus)
        self.btn_remdupes.setFocusPolicy(Qt.NoFocus)
        self.btn_screenshot.setFocusPolicy(Qt.NoFocus)
        self.btn_clear.setFocusPolicy(Qt.NoFocus)

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

    def replace_all_text(self, new_text):
        # Like setPlainText but recorded as one undo step, so Ctrl+Z brings back the old text
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.Document)
        cursor.insertText(new_text)
        cursor.endEditBlock()
        self.setTextCursor(cursor)
        self.setFocus() # Ctrl+Z goes here right away

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

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.panel_width = 260 # full width of the calculator when expanded
        self.setFixedWidth(0) # starts closed - MainWindow animates this

        self.text_box = QLineEdit()
        self.text_box.setFont(QFont("Cascadia Code", 32))

        self.text_box.setReadOnly(True) # view and copy only - typing goes through the buttons
        self.text_box.installEventFilter(self) # let the Calculator see the display's key presses first

        self.operators = "+-x/"
        self.button_map = {} # button text -> button, so a key press can find its button

        self.grid = QGridLayout()

        self.buttons = [
            "7", "8", "9", "/",
            "4", "5", "6", "x",
            "1", "2", "3", "-",
            "0", ".", "=", "+"
        ]

        # The FOR LOOP
        row = 0
        col = 0

        for text in self.buttons:
            button = QPushButton(text)
            button.setStyleSheet("QPushButton {font: 25px Cascadia Code; padding: 10px;}")
            button.setFocusPolicy(Qt.NoFocus) # keep the cursor in the display
            button.clicked.connect(self.button_click)
            self.button_map[text] = button
            self.grid.addWidget(button, row, col)
            col += 1
            if col > 3: # after 4 buttons, go back to column 0 on the next row
                col = 0
                row += 1

        self.btn_clear = QPushButton("Clear")
        self.btn_delete = QPushButton()
        self.btn_delete.setIcon(QIcon(resource_path(os.path.join("icons", "delete.png"))))
        self.btn_delete.setIconSize(QSize(25, 25))
        self.btn_clear.setStyleSheet("QPushButton {font: 15px Cascadia Code; padding: 5px;}")
        self.btn_delete.setStyleSheet("QPushButton {font: 15px Cascadia Code; padding: 5px;}")
        self.btn_clear.setFocusPolicy(Qt.NoFocus)
        self.btn_delete.setFocusPolicy(Qt.NoFocus)
        self.btn_clear.clicked.connect(self.button_click)
        self.btn_delete.clicked.connect(self.button_click)
        self.button_map["Clear"] = self.btn_clear
        self.button_map["<"] = self.btn_delete

        # Short "pressed" flash when a button is triggered from the keyboard
        self.flash_timer = QTimer(self)
        self.flash_timer.setSingleShot(True)
        self.flash_timer.timeout.connect(self.release_buttons)

        button_row = QHBoxLayout()
        button_row.addWidget(self.btn_clear)
        button_row.addWidget(self.btn_delete)

        master_layout = QVBoxLayout()
        master_layout.setContentsMargins(10, 10, 10, 10)
        master_layout.addWidget(self.text_box)
        master_layout.addLayout(self.grid)
        master_layout.addLayout(button_row)
        master_layout.addStretch() # keeps the calculator at the top when the window gets taller

        self.panel = QWidget(self)
        self.panel.setFixedWidth(self.panel_width)
        self.panel.setLayout(master_layout)

    def resizeEvent(self, event):
        # Keep the inner pannel as tall as the Calculator widget
        self.panel.resize(self.panel_width, self.height())
        super().resizeEvent(event)

    def eventFilter(self, obj, event):
        # Every event for the display passes through here before the display gets it
        if obj == self.text_box and event.type() == QEvent.KeyPress:
            key_text = self.key_to_button_text(event)

            if key_text in self.button_map:
                self.flash_button(self.button_map[key_text])
                self.press(key_text)
                return True # handled - the display never sees this key

        return super().eventFilter(obj, event) # anything else (Ctrl+C, arrows...) works as normal

    def key_to_button_text(self, event):
        key_text = event.text()

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            key_text = "="
        elif event.key() == Qt.Key_Escape:
            key_text = "Clear"
        elif event.key() == Qt.Key_Backspace:
            key_text = "<"
        elif key_text == "*" or key_text == "X":
            key_text = "x"
        elif key_text == ",": # decimal key
            key_text = "."

        return key_text

    def flash_button(self, button):
        self.release_buttons() # in case the previous flash is still showing
        button.setDown(True)
        self.flash_timer.start(100)

    def release_buttons(self):
        for button in self.button_map.values():
            button.setDown(False)

    def button_click(self):
        button = self.sender() # which button was clicked

        if button == self.btn_delete:
            self.press("<")
        else:
            self.press(button.text())

        self.text_box.setFocus() # clicking the calculator sends typing to the calculator

    def current_number(self, expression):
        # The number being typed right now = everything after the last operator
        number = ""
        for char in reversed(expression):
            if char in self.operators:
                break
            number = char + number
        return number

    def press(self, text):
        current_value = self.text_box.text()

        # After and error, the next press starts fresh
        if current_value == "Error":
            current_value = ""

        if text == "=":
            symbol = current_value.replace("x", "*")
            try:
                res = eval(symbol)

                # Fixing 0.3000000004 -> 0.3 and 3.0 -> 3
                if isinstance(res, float):
                    res = round(res, 10)
                    if res.is_integer() and abs(res) < 1e15:
                        res = int(res)

                current_value = str(res)
            except Exception as e:
                print("Error:", e)
                current_value = "Error"

        elif text == "Clear":
            current_value = ""

        elif text == "<":
            current_value = current_value[:-1]

        elif text in self.operators:
            # Fixing two operators in a row replacing each other, so (** = power)
            if current_value == "":
                if text == "-":
                    current_value = "-" # a negative number can start with -
            elif current_value[-1] in self.operators:
                if current_value != "-":
                    current_value = current_value[:-1] + text
            else:
                current_value += text

        elif text == ".":
            number = self.current_number(current_value)
            if "." in number:
                pass # a number can only have one decimal point
            elif number == "":
                current_value += "0." # "." on its own becomes "0."
            else:
                current_value += "."

        else: # a digit
            # Fixing 05 -> 5
            if self.current_number(current_value) == "0":
                current_value = current_value[:-1] + text
            else:
                current_value += text

        self.text_box.setText(current_value)
