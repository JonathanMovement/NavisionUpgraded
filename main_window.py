import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QVariantAnimation, QEasingCurve, QAbstractAnimation
from PyQt5.QtGui import QIcon
from logic import resource_path
from widgets import TopBar, SideBar, PlainTextEdit, Calculator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("NavisionUpgraded")
        self.resize(700, 500)
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon(resource_path(os.path.join("icons", "KTNlogo.ico"))))

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
            self.top_bar.btn_expand.setText(">>")
            self.top_bar.btn_expand.setToolTip("Expand window")
        else:
            self.expanded = True
            self.top_bar.btn_expand.setText("<<")
            self.top_bar.btn_expand.setToolTip("Shrink window")
            self.calculator.text_box.setFocus()





