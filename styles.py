# UI_COLORS
GRAPHITE_BLACK = "#27292b"
CARBON_SHELL = "#1f2021"
DARK_MATTER = "#020203"
ANVIL = "#4a4c4f"
PLATINUM_CORE = "#8d8f91"
CRIMSON_VOID = "#42070d"
CARBON_CRIMSON = "#c93847"
DEEP_VELVET = "#271729"
DARK_NEBULA = "#1a0a1c"
CONSOLE_BLUE = "#181b24"
OBSIDIAN = "#161718"
FROST_WHITE = "#e8e8ea"
CRIMSON_GLOW = "#e04656" 
VELVET_EDGE = "#3a2340"   
GLITCH_CYAN = "#20e3ff"
NIGHT_INK = "#121314"

APP_STYLE = f"""
        QMainWindow, QDialog {{
            background-color: {CARBON_SHELL}
        }}
        QWidget {{
            color: {FROST_WHITE};
        }}
        #TopBar {{
            background-color: {OBSIDIAN};
            border-bottom: 1px solid {GRAPHITE_BLACK};
            color: {FROST_WHITE};
            border: 1px solid {ANVIL};
            border-radius: 6px;
            padding: 6px 4px;
            font-family
        }}
        QPushButton {{
            background-color: {GRAPHITE_BLACK};
            color: {FROST_WHITE};
            border: 1px solid {ANVIL};
            border-radius: 6px;
            padding: 6px 4px;
            font-family: "Cascadia Code";
            font-size: 13px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {ANVIL};
            border-color: {PLATINUM_CORE};
        }}

        QPushButton[kind="digit"] {{
            font-size: 22px;
            padding: 10px;
        }}
        QPushButton[kind="operator"] {{
            background-color": {DEEP_VELVET};
            border-color: {VELVET_EDGE};
            color: {CARBON_CRIMSON};
            font-size: 22px;
            padding: 10px;
        }}
        QPushButton[kind="operator"]:hover {{
            background-color: {VELVET_EDGE};
        }}
        QPushButton[kind="equals"] {{
            background-color: {CARBON_CRIMSON};
            border-color: {CARBON_CRIMSON};
            color: white;
            font-size: 22px;
            padding: 10px;
        }}
        QPushButton[kind="equals"]:hover {{
            background-color: {CRIMSON_GLOW};
        }}
        QPushButton[kind="danger"]:hover {{
            background-color: {CRIMSON_VOID};
            border-color: #6b0f18;
        }}
        QPushButton[kind="danger"]:hover {{
            background-color: #5c0a13;
        }}
        QPushButton:pressed {{
            background-color: {CARBON_CRIMSON};
            border-color: {CRIMSON_GLOW};
            color: white;
        }}
        #TextArea {{
            background-color: {GRAPHITE_BLACK};
            border: 1px solid {GRAPHITE_BLACK};
            border-radius: 8px;
            padding: 6px;
            selection-background-color: {CARBON_CRIMSON};
        }}
        #TextArea:focus {{
            border: 1px solid {CARBON_CRIMSON};
        }}

        #CalcPanel {{
            background-color: {OBSIDIAN};
            border-left: 1px solid {GRAPHITE_BLACK};
        }}
        #CalcDisplay {{
            background-color: {DARK_MATTER};
            border: 1px solid {GRAPHITE_BLACK};
            border-radius: 8px;
            padding: 4px 8px;
            selection-background-color: {CARBON_CRIMSON};
        }}
        #CalcDisplay:focus {{
            border: 1px solid {CARBON_CRIMSON};
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 2px;
        }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 10px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
            background: {ANVIL};
            border-radius: 3px;
            min-height: 30px;
            min-width: 30px;
        }}
        QScrollBar::handle::vertical, QScrollBar::handle:horizontal {{
            background: {ANVIL};
            border-radius: 3px;
            min-height: 30px;
            min-width: 30px;
        }}
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
            background: {PLATINUM_CORE};
        }}
        QScrollBar::add-line, QScrollBar::sub-line {{
            width: 0px;
            height: 0px;
        }}
        QScrollBar::add-page, QScrollBar::sub-page {{
            background: none;
        }}
        QToolTip {{
            background-color: {DARK_MATTER};
            color: {FROST_WHITE};
            border: 1px solid {ANVIL};
            padding: 4px;
        }}
        QMessageBox QPushButton {{
            min-width: 70px;
        }}
    """