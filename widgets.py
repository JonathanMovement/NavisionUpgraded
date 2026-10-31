from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, 
                             QLineEdit, QGridLayout, QLabel)
from PyQt5.QtCore import Qt, QRectF, QTimer, QSize, QEvent, QElapsedTimer
from PyQt5.QtGui import QPainter, QFont, QColor, QPixmap, QIcon, QTextCursor, QImage
from logic import resource_path
import os
import random
from styles import CARBON_CRIMSON, GLITCH_CYAN, FROST_WHITE

# 5 x 7 pixel font - "X" = lit pixel. Only the letters NAVISION needs.
PIXEL_FONT = {
    "N": ["X...X",
          "XX..X",
          "X.X.X",
          "X..XX",
          "X...X",
          "X...X",
          "X...X"],
    "A": [".XXX.",
          "X...X",
          "X...X",
          "XXXXX",
          "X...X",
          "X...X",
          "X...X"],
    "V": ["X...X",
          "X...X",
          "X...X",
          "X...X",
          "X...X",
          ".X.X.",
          "..X.."],
    "I": [".XXX.",
          "..X..",
          "..X..",
          "..X..",
          "..X..",
          "..X..",
          ".XXX."],
    "S": [".XXXX",
          "X....",
          "X....",
          ".XXX.",
          "....X",
          "....X",
          "XXXX."],
    "O": [".XXX.",
          "X...X",
          "X...X",
          "X...X",
          "X...X",
          "X...X",
          ".XXX."],
}

class NavisionTitle(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.word = "NAVISION"
        self.setMinimumHeight(56)

        # Size of the pixel letters
        self.block = 5      # one font pixel = 5x5 screen pixels
        self.letter_gap = 2 # empty font pixels between letters

        # Panel width
        word_width = (7 + self.letter_gap) * self.block * len(self.word) - self.letter_gap * self.block
        self.setFixedWidth(word_width + 50)

        # Magnifying glass
        self.max_zoom = 0.5   # the letter under the lens grows to 1.5x
        self.lens_speed = 3.0 # letters per second

        # Glitch
        self.glitch_until = 0.0 # time when the current glitch burst ends
        self.next_glitch = 2.0  # time when the next glitch burst starts
        self.slices = []        # (y, height, x_offset) bands while glitching

        # Colors
        self.color_text = QColor(FROST_WHITE)
        self.color_red = QColor(CARBON_CRIMSON)
        self.color_cyan = QColor(GLITCH_CYAN)

        # Animation clock: positions come from real elapsed time.
        self.clock = QElapsedTimer()
        self.clock.start()

        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.tick)
        self.timer.start(16) # ~60 frames per second

    def now(self):
        return self.clock.elapsed() / 1000.0 # seconds since the app started

    def tick(self):
        t = self.now()

        # Time for a new glitch burst?
        if t >= self.next_glitch:
            self.glitch_until = t + random.uniform(0.12, 0.35)
            self.next_glitch = t + random.uniform(2.0, 5.0)

        # While glitching, cut the word into random horizontal bands every frame
        self.slices = []

        if t < self.glitch_until:
            y = 0
            while y < self.height():
                band = random.randint(4, 14)
                offset = 0
                if random.random() < 0.35:
                    offset = random.randint(-7, 7)
                self.slices.append((y, band, offset))
                y += band

        self.update()

    def lens_position(self):
        # Moves from -1 (left of the first letter) to len + 1 (right of the last), then repeats
        travel = len(self.word) + 2
        return (self.now() * self.lens_speed) % travel - 1

    def letter_scale(self, index):
        distance = abs(index - self.lens_position())
        strength = max(0.0, 1.0 - distance)
        return 1.0 + self.max_zoom * strength

    def render_word(self, color):
        # Draws the whole word as pixel blocks into a transparent image
        ratio = self.devicePixelRatioF()
        image = QImage(int(self.width() * ratio), int(self.height() * ratio), QImage.Format_ARGB32_Premultiplied)
        image.setDevicePixelRatio(ratio)
        image.fill(Qt.transparent)

        painter = QPainter(image)
        cell = (5 + self.letter_gap) * self.block # width of one letter + gap
        total_width = cell * len(self.word) - self.letter_gap * self.block
        start_x = (self.width() - total_width) / 2
        center_y = self.height() / 2

        for index in range(len(self.word)):
            rows = PIXEL_FONT[self.word[index]]
            size = self.block * self.letter_scale(index) # bigger blocks under the lens
            center_x = start_x + index * cell + 5 * self.block / 2
            left = center_x - 5 * size / 2
            top = center_y - 7 * size / 2

            for row in range(7):
                for col in range(5):
                    if rows[row][col] == "X":
                        # Whole pixels only, with a 1 pixel gap between "LEDs"
                        x = round(left + col * size)
                        y = round(top + row * size)
                        lit = max(1, round(size) -1)
                        painter.fillRect(x, y, lit, lit, color)

        painter.end()
        return image

    def draw_layer(self, painter, image, shift):
        # Draws one colored copy of the word, cut into glitch bands if a glitch is running
        if len(self.slices) == 0:
            painter.drawImage(shift, 0, image)
            return

        ratio = image.devicePixelRatio()
        for y, band, offset in self.slices:
            source = QRectF(0, y * ratio, image.width(), band * ratio)
            target = QRectF(shift + offset, y, self.width(), band)
            painter.drawImage(target, image, source)

    def paintEvent(self, event):
        painter = QPainter(self)

        glitching = len(self.slices) > 0
        split = 1
        if glitching:
            split = 4

        painter.setCompositionMode(QPainter.CompositionMode_Plus)
        self.draw_layer(painter, self.render_word(self.color_red), -split)
        self.draw_layer(painter, self.render_word(self.color_cyan), split)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        self.draw_layer(painter, self.render_word(self.color_text), 0)

        painter.end()

class TopBar(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setObjectName("TopBar")
        self.setFixedHeight(70)
        self.setAttribute(Qt.WA_StyledBackground, True)

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
        layout.addStretch()
        layout.addWidget(self.title)
        layout.addStretch()
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
        self.word_count = QLabel()
        self.word_count.setAlignment(Qt.AlignCenter)
        self.word_count.setStyleSheet("font-family: Cascadia Code;"
                                      "font-size: 15px;")
        self.word_count.setWordWrap(True)
        self.word_count.hide()
        self.btn_clear = QPushButton()
        self.btn_clear.setIcon(QIcon(resource_path(os.path.join("icons", "broom.png"))))
        self.btn_clear.setIconSize(QSize(30, 30))
        self.btn_clear.setProperty("kind", "danger") # dark red

        # SideBar button height
        self.btn_filter_1.setFixedHeight(38)
        self.btn_filter_2.setFixedHeight(38)
        self.btn_filter_3.setFixedHeight(38)
        self.btn_remdupes.setFixedHeight(38)

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
        layout.addWidget(self.word_count)
        layout.addWidget(self.btn_clear)

class PlainTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setObjectName("TextArea")
        self.setPlaceholderText("Paste your text here ^-^\nCTRL+Z -> Undo\nCTRL+Y -> Redo\n\n" \
        "WinOCR limits:\nUnderscores and other symbols are not supported/read by WinOCR.\n" \
        "It sometimes autocorrects letter 'l' to 1, always double check.")

        text_font = QFont("Cascadia Code")
        text_font.setPixelSize(15)
        self.setFont(text_font)

        # Background image
        self.bg_original = QPixmap(resource_path(os.path.join("icons", "KatoenNatie.png")))
        self.bg_scaled = None
        self.bg_scaled_for = None # the size the cached copy was made for
        self.bg_opacity = 1.0

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
            painter.setOpacity(self.bg_opacity)
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
        self.text_box.setObjectName("CalcDisplay")
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

            if text == "=":
                button.setProperty("kind", "equals")
            elif text in self.operators:
                button.setProperty("kind", "operator")
            else:
                button.setProperty("kind", "digit")

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
        self.btn_clear.setProperty("kind", "danger")
        self.btn_delete.setProperty("kind", "danger")
        self.btn_clear.setFocusPolicy(Qt.NoFocus)
        self.btn_delete.setFocusPolicy(Qt.NoFocus)
        self.btn_clear.clicked.connect(self.button_click)
        self.btn_delete.clicked.connect(self.button_click)
        self.button_map["Clear"] = self.btn_clear
        self.button_map["<"] = self.btn_delete
        self.slogan = QLabel("Our people make the difference.")
        self.slogan.setStyleSheet("font-size: 12px;"
                                  "font-family: Cascadia Code;"
                                  "font-weight: bold;")
        self.slogan.setAlignment(Qt.AlignCenter)
        self.slogan.setWordWrap(True)
        

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
        master_layout.addSpacing(14)
        master_layout.addWidget(self.slogan)
        master_layout.addStretch() # keeps the calculator at the top when the window gets taller

        self.panel = QWidget(self)
        self.panel.setObjectName("CalcPanel")
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