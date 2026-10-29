APP_STYLES = """
QMainWindow, QWidget#appRoot, QWidget#pageBg { background: #fffdf5; color: #191919; }
QFrame#topHeader { background: #ffcc00; border-bottom: 4px solid #111111; }
QLabel#brandTitle { font-size: 20px; font-weight: 900; color: #111111; }
QLabel#brandSubtitle { font-size: 13px; color: #28220a; }
QLabel#sessionBadge { background: #111111; color: #ffcc00; border-radius: 10px;
                      padding: 5px 12px; font-weight: 800; font-size: 11px; }
QPushButton#headerButton { background: #ffdc45; border: 1px solid #e3b900; border-radius: 9px;
                           padding: 9px 14px; font-weight: 800; color: #111111; }
QPushButton#headerButton:hover { background: #ffe77c; }
QPushButton#signOutButton { background: #111111; border: 1px solid #111111; border-radius: 9px;
                            padding: 9px 14px; font-weight: 800; color: #ffcc00; }
QPushButton#signOutButton:hover { background: #333333; }
QFrame#footer { background: #ffcc00; border-top: 4px solid #111111; }
QLabel#footerText { font-size: 11px; font-weight: 800; color: #171717; }

/* ---- selection / login pages ---- */
QLabel#pageTitle { font-size: 26px; font-weight: 900; color: #111111; }
QLabel#pageSub { font-size: 13px; color: #5b5b5b; }
QPushButton#choiceButton { background: #ffffff; border: 2px solid #111111; border-radius: 14px;
                           padding: 18px 20px; font-size: 16px; font-weight: 800; color: #111111; text-align: left; }
QPushButton#choiceButton:hover { background: #ffcc00; }
QPushButton#primaryButton { background: #ffcc00; border: 1px solid #e4b700; border-radius: 9px;
                            padding: 11px 16px; font-weight: 800; color: #111111; font-size: 13px; }
QPushButton#primaryButton:hover { background: #ffe066; }
QPushButton#linkButton { background: transparent; border: none; color: #6b5900; font-weight: 700; padding: 6px; }
QPushButton#linkButton:hover { color: #111111; text-decoration: underline; }
QLabel#fieldLabel { font-size: 11px; font-weight: 800; color: #4a4a4a; letter-spacing: 1px; }
QLabel#fieldHint { font-size: 11px; color: #8a8a8a; }
QLabel#statusError { color: #c4171d; font-weight: 700; font-size: 12px; }
QLineEdit#field { border: 1px solid #cfc8b4; border-radius: 8px; padding: 9px 11px; background: white;
                  color: #111; font-size: 14px; }
QLineEdit#field:focus { border: 2px solid #ffcc00; }
QPushButton#eyeButton { border: 1px solid #cfc8b4; border-left: none; background: #faf8f0;
                        border-top-right-radius: 8px; border-bottom-right-radius: 8px; }

/* ---- heatmap page ---- */
QFrame#sidebar { background: #fffdf5; border-right: 1px solid #e5dcc2; }
QLabel#sectionTitle { font-size: 20px; font-weight: 900; color: #171717; }
QLabel#sectionSub { font-size: 10px; color: #8a7100; font-weight: 800; letter-spacing: 1px; }
QPushButton#floorButton { text-align: left; background: #ffffff; color: #242424;
 border: 1px solid #e7dfcb; border-left: 4px solid #e7dfcb; border-radius: 9px;
 padding: 12px 10px; font-size: 12px; font-weight: 600; min-height: 48px; }
QPushButton#floorButton:hover { background: #fff4bd; border-color: #e8c000; }
QPushButton#floorButton:checked { background: #ffcc00; border: 1px solid #e5b900;
 border-left: 5px solid #111111; color: #111111; font-weight: 900; }
QLabel#legendTitle { font-weight: 800; font-size: 12px; }
QFrame#legendCard { background: #fff6d5; border: 1px solid #f0e4b8; border-radius: 8px; }
QLabel#modeNote { font-size: 11px; color: #5b4b00; background: #fff6d5; border: 1px solid #f0e4b8;
                  border-radius: 8px; padding: 8px; }
"""

DIALOG_STYLES = """
QDialog { background: #fffdf5; }
QLabel#title { color: #171717; font-size: 20px; font-weight: 700; }
QLabel#sub { color: #5b5b5b; font-size: 12px; }
QLabel#prompt { color: #333333; font-size: 12px; font-weight: 600; }
QLabel#ok { color: #2e7d00; font-weight: 700; font-size: 12px; }
QLabel { color: #171717; font-size: 13px; }
QLineEdit { border: 1px solid #cfc8b4; border-radius: 7px; padding: 11px; background: #ffffff;
            color: #111111; font-size: 14px; }
QListWidget { border: 1px solid #cfc8b4; border-radius: 7px; background: #ffffff; color: #111; font-size: 13px; }
QListWidget::item { padding: 8px; }
QListWidget::item:selected { background: #ffcc00; color: #111; }
QTimeEdit, QSpinBox { border: 1px solid #cfc8b4; border-radius: 7px; padding: 4px 6px; background: #ffffff;
                      color: #111111; font-size: 13px; min-width: 95px; min-height: 28px; }
QCalendarWidget { background-color: #ffffff; border: 1px solid #cfc8b4; border-radius: 8px; }
QCalendarWidget QWidget#qt_calendar_navigationbar { background-color: #ffcc00; }
QCalendarWidget QToolButton { color: #111111; font-weight: bold; background: transparent; border: none; margin: 2px; }
QCalendarWidget QToolButton:hover { background-color: #ffe066; border-radius: 4px; }
QCalendarWidget QMenu { background-color: #ffffff; color: #111111; }
QCalendarWidget QAbstractItemView:enabled { color: #111111; background-color: #ffffff;
    selection-background-color: #ffcc00; selection-color: #111111; font-size: 12px; }
QPushButton { background: #ffcc00; border: 1px solid #e4b700; border-radius: 7px; padding: 10px 14px;
              font-weight: 700; color: #111111; }
QPushButton:hover { background: #ffe066; }
QPushButton#secondary, QPushButton#cancel { background: #ffffff; border: 1px solid #d7d0bd; }
QPushButton#secondary:hover, QPushButton#cancel:hover { background: #f7f4ea; }
QPushButton#danger { background: #ff575d; border: 1px solid #d93a40; color: white; }
QPushButton#danger:hover { background: #ff7479; }
"""

MESSAGEBOX_STYLES = """
QMessageBox { background: #fffdf5; }
QMessageBox QLabel { color: #171717; font-size: 13px; }
QPushButton { background: #ffcc00; border: 1px solid #e4b700; border-radius: 7px; padding: 7px 18px;
              font-weight: 700; color: #111111; min-width: 70px; }
QPushButton:hover { background: #ffe066; }
"""
