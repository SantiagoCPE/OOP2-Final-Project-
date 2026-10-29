import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget,
                             QVBoxLayout, QWidget)

from core import auth
from core.seat_manager import SeatManager
from ui.common import ask_yes_no
from ui.heatmap_page import ASSETS, HeatmapPage
from ui.pages import AdminLoginPage, AdminTypePage, RolePage, StudentLoginPage
from ui.support_dialog import SupportDialog
from ui.theme import APP_STYLES


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TIP Integrated Library Services | Library Space Heat Map")
        self.resize(1240, 760)
        self.setMinimumSize(1000, 650)
        self.setStyleSheet(APP_STYLES)
        self.seat_manager = SeatManager()
        self.heatmap = None

        root = QWidget(); root.setObjectName("appRoot")
        outer = QVBoxLayout(root); outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)
        outer.addWidget(self._build_header())

        self.stack = QStackedWidget()
        self.role_page, self.admin_type_page = RolePage(), AdminTypePage()
        self.student_login, self.admin_login = StudentLoginPage(), AdminLoginPage()
        for page in (self.role_page, self.admin_type_page, self.student_login, self.admin_login):
            self.stack.addWidget(page)
        outer.addWidget(self.stack, 1)

        footer = QFrame(); footer.setObjectName("footer"); footer.setFixedHeight(42)
        fl = QHBoxLayout(footer)
        ft = QLabel("© 2026 Technological Institute of the Philippines. All Rights Reserved.")
        ft.setObjectName("footerText"); ft.setAlignment(Qt.AlignmentFlag.AlignCenter); fl.addWidget(ft)
        outer.addWidget(footer)
        self.setCentralWidget(root)

        self.role_page.student_chosen.connect(self.show_student_login)
        self.role_page.admin_chosen.connect(lambda: self.stack.setCurrentWidget(self.admin_type_page))
        self.admin_type_page.back.connect(self.show_role)
        self.admin_type_page.librarian_chosen.connect(lambda: self.show_admin_login("librarian"))
        self.admin_type_page.entrance_chosen.connect(lambda: self.show_admin_login("entrance"))
        self.student_login.back.connect(self.show_role)
        self.admin_login.back.connect(lambda: self.stack.setCurrentWidget(self.admin_type_page))
        self.student_login.logged_in.connect(lambda num: self.open_heatmap("student", num, f"Student  {num}"))
        self.admin_login.logged_in.connect(
            lambda kind, user: self.open_heatmap(kind, None, f"{auth.ADMIN_LABELS[kind]}  ·  {user}"))
        self.show_role()

    def _build_header(self):
        header = QFrame(); header.setObjectName("topHeader"); header.setFixedHeight(84)
        lay = QHBoxLayout(header); lay.setContentsMargins(24, 10, 24, 10); lay.setSpacing(16)
        logo = QLabel(); logo.setFixedSize(76, 58); logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = QPixmap(os.path.join(ASSETS, "tip_logo.png"))
        if not pix.isNull():
            logo.setPixmap(pix.scaled(76, 58, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation))
        logo.setStyleSheet("background:white;border:1px solid #111")
        brand = QVBoxLayout(); brand.setSpacing(2)
        t = QLabel("TECHNOLOGICAL INSTITUTE OF THE PHILIPPINES"); t.setObjectName("brandTitle")
        s = QLabel("Integrated Library Services"); s.setObjectName("brandSubtitle")
        brand.addWidget(t); brand.addWidget(s)
        lay.addWidget(logo); lay.addLayout(brand, 1)
        self.session_badge = QLabel(""); self.session_badge.setObjectName("sessionBadge"); self.session_badge.hide()
        support = QPushButton("🎧  Support"); support.setObjectName("headerButton")
        support.setCursor(Qt.CursorShape.PointingHandCursor); support.clicked.connect(self.open_support)
        self.sign_out_btn = QPushButton("⎋  Sign out of the app"); self.sign_out_btn.setObjectName("signOutButton")
        self.sign_out_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sign_out_btn.clicked.connect(self.sign_out); self.sign_out_btn.hide()
        lay.addWidget(self.session_badge); lay.addWidget(support); lay.addWidget(self.sign_out_btn)
        return header

    # ---------- navigation ----------
    def show_role(self):
        self.stack.setCurrentWidget(self.role_page)

    def show_student_login(self):
        self.student_login.reset()
        self.stack.setCurrentWidget(self.student_login)

    def show_admin_login(self, kind):
        self.admin_login.set_kind(kind)
        self.stack.setCurrentWidget(self.admin_login)

    def open_heatmap(self, mode, student_number, badge_text):
        self._close_heatmap()
        self.heatmap = HeatmapPage(mode, self.seat_manager, student_number)
        self.stack.addWidget(self.heatmap)
        self.stack.setCurrentWidget(self.heatmap)
        self.session_badge.setText(badge_text); self.session_badge.show()
        self.sign_out_btn.show()

    def _close_heatmap(self):
        if self.heatmap is not None:
            self.heatmap.stop()
            self.stack.removeWidget(self.heatmap)
            self.heatmap.deleteLater()
            self.heatmap = None

    def sign_out(self):
        info = ""
        if not ask_yes_no(self, "Sign out", "Sign out of the app?", info):
            return
        self._close_heatmap()
        self.session_badge.hide(); self.sign_out_btn.hide()
        self.show_role()

    # ---------- support ----------
    def open_support(self):
        mode = self.heatmap.mode if self.heatmap else None
        text = {
            "student": "For account problems, approach the library desk. Use Refresh Screen if the seat colours look out of date.",
            "entrance": "Entrance access can only log students in and out of chairs. Use Refresh Screen if the map looks out of date.",
            "librarian": "Librarian access can remove reservations from yellow chairs. Use Refresh Screen if the map looks out of date.",
            None: "For account access or password assistance, contact the library support desk.",
        }[mode]
        refresh = self.heatmap.force_refresh if self.heatmap else (lambda: False)
        SupportDialog(text, refresh, self).exec()
