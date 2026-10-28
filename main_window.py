import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from logic import resource_path
from widgets import TopBar, SideBar, PlainTextEdit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("NavisionUpgraded")
        self.resize(700, 600)
        self.setMinimumSize(600, 500)
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

        body_layout.addWidget(self.side_bar)
        body_layout.addWidget(self.text_area, 1)

        main_layout.addWidget(self.top_bar)
        main_layout.addLayout(body_layout, 1)




