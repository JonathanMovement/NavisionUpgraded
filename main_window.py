import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QVariantAnimation, QEasingCurve, QAbstractAnimation
from PyQt5.QtGui import QIcon, QImage, QPainter
from logic import resource_path, filter_1, filter_2, filter_3, remove_duplicates, ocr_image, ocr_max_image_size
from widgets import TopBar, SideBar, PlainTextEdit, Calculator
import sys
import ctypes
from styles import OBSIDIAN, FROST_WHITE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("NavisionUpgraded")
        self.resize(700, 500)
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon(resource_path(os.path.join("icons", "KTNlogo.ico"))))

        self.dark_title_bar()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout: top bar above, body below
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        # Body: side bar | text area | calculator
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.top_bar = TopBar()
        self.side_bar = SideBar()
        self.text_area = PlainTextEdit()
        self.calculator = Calculator()
        self.calculator.hide() # closed when the app starts

        body_layout.addWidget(self.side_bar)
        body_layout.addWidget(self.text_area, 1)
        body_layout.addWidget(self.calculator)

        main_layout.addWidget(self.top_bar)
        main_layout.addLayout(body_layout, 1)

        # Expand / shrink animation
        self.expanded = False
        self.base_width = self.width() # window width without the calculator

        self.expand_anim = QVariantAnimation(self)
        self.expand_anim.setDuration(300) # milliseconds
        self.expand_anim.setEasingCurve(QEasingCurve.InOutCubic) # slow start, fast middle, slow end

        # Connections / signals
        self.expand_anim.valueChanged.connect(self.animation_step)
        self.expand_anim.finished.connect(self.animation_finished)
        self.top_bar.btn_expand.clicked.connect(self.toggle_calculator)
        self.side_bar.btn_filter_1.clicked.connect(self.apply_filter_1)
        self.side_bar.btn_filter_2.clicked.connect(self.apply_filter_2)
        self.side_bar.btn_filter_3.clicked.connect(self.apply_filter_3)
        self.side_bar.btn_remdupes.clicked.connect(self.apply_remove_duplicates)
        self.side_bar.btn_clear.clicked.connect(self.clear_text)
        self.side_bar.btn_screenshot.clicked.connect(self.read_clipboard)

    def toggle_calculator(self):
        # Ignore clicks while the window is still moving
        if self.expand_anim.state() == QAbstractAnimation.Running:
            return

        if self.expanded:
            start = self.calculator.panel_width
            end = 0
            self.text_area.setFocus() # move the cursor out before the calculator disappears
        else:
            start = 0
            end = self.calculator.panel_width
            self.calculator.show()

        # Whatever the window width is right now (even after manual resizing), except the calculator
        self.base_width = self.width() - start

        self.expand_anim.setStartValue(start)
        self.expand_anim.setEndValue(end)
        self.expand_anim.start()

    def animation_step(self, calc_width):
        self.calculator.setFixedWidth(calc_width)

        # A maximized window can't grow - the calculator just takes space from the text area
        if not self.isMaximized():
            self.resize(self.base_width + calc_width, self.height())

    def animation_finished(self):
        if self.expanded:
            self.calculator.hide()
            self.expanded = False
            self.top_bar.btn_expand.setToolTip("Expand window")
        else:
            self.expanded = True
            self.top_bar.btn_expand.setToolTip("Shrink window")
            self.calculator.text_box.setFocus()

    def apply_filter_1(self):
        text = self.text_area.toPlainText()
        self.text_area.replace_all_text(filter_1(text))

    def apply_filter_2(self):
        text = self.text_area.toPlainText()
        self.text_area.replace_all_text(filter_2(text))

    def apply_filter_3(self):
        text = self.text_area.toPlainText()
        self.text_area.replace_all_text(filter_3(text)) 

    def apply_remove_duplicates(self):
        text = self.text_area.toPlainText()
        self.text_area.replace_all_text(remove_duplicates(text))

    def clear_text(self):
        self.text_area.replace_all_text("")   

    def read_clipboard(self):
        image = QApplication.clipboard().image()

        if image.isNull():
            QMessageBox.warning(self, "Clipboard empty",
                                "No image in clipboard.\nTake a screenshot with Win + Shift + S first.")
            return

        QApplication.setOverrideCursor(Qt.WaitCursor) # spinning cursor while OCR runs
        try:
            # Double the size if it still fits - small text is read better when it's bigger
            margin = 20
            max_size = ocr_max_image_size()
            if image.width() * 2 + margin * 2 <= max_size and image.height() * 2 + margin * 2 <= max_size:
                image = image.scaled(image.width() * 2, image.height() * 2,
                                     Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

            # White margin around the picture
            bordered = QImage(image.width() + margin * 2, image.height() + margin * 2, QImage.Format_RGBA8888)
            bordered.fill(Qt.white)
            painter = QPainter(bordered)
            painter.drawImage(margin, margin, image)
            painter.end()
            image = bordered

            # Windows OCR wants raw pixels as R, G, B, A bytes
            image = image.convertToFormat(QImage.Format_RGBA8888)
            data = image.bits().asstring(image.sizeInBytes())

            text = ocr_image(data, image.width(), image.height())
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Screenshot -> Text failed", str(e))
            return

        QApplication.restoreOverrideCursor()
        self.text_area.replace_all_text(text) # undoable with Ctrl+Z

    def dark_title_bar(self):
        if sys.platform != "win32":
            return

        hwnd = int(self.winId()) # the window's Windows handle
        dark_mode = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode))

        caption = ctypes.c_int(self.to_colorref(OBSIDIAN))
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(caption), ctypes.sizeof(caption))

        title_text = ctypes.c_int(self.to_colorref(FROST_WHITE))
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 36, ctypes.byref(title_text), ctypes.sizeof(title_text))

    def to_colorref(self, hex_color):
        red = int(hex_color[1:3], 16)
        green = int(hex_color[3:5], 16)
        blue = int(hex_color[5:7], 16)
        return (blue << 16) | (green << 8) | red






