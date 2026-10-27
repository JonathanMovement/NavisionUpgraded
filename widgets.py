from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QFont, QColor

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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setFont(self.title_font)
        painter.setPen(QColor("#333333"))

        # Center the word horizontally
        total_width = self.letter_width * len(self.word)
        x = (self.width() - total_width) / 2

        for letter in self.word:
            cell = QRectF(x, 0, self.letter_width, self.height())
            painter.drawText(cell, Qt.AlignCenter, letter)
            x += self.letter_width

        painter.end()

class TopBar(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setObjectName("TopBar")
        self.setFixedHeight(60)
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


