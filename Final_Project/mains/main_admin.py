import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QFrame, QGraphicsOpacityEffect, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QSizePolicy,
    QStackedWidget, QVBoxLayout, QWidget, QFileDialog,
)
from main_library import LibraryLoginForm

BASE_DIR = Path(__file__).resolve().parent


class LoginForm(QWidget):
    """Reusable login form; its signals/actions are kept separate from styling."""

    def __init__(self, mode: str, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.password_visible = False
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.form = QWidget()
        self.form.setObjectName("loginForm")
        form_layout = QVBoxLayout(self.form)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(6)

        if self.mode == "student":
            identity_label = "STUDENT NUMBER"
            identity_placeholder = "2024-12345"
            button_text = "ACCESS SPACE HEATMAP  →"
        else:
            identity_label = "ADMIN USERNAME / ID"
            identity_placeholder = "admin.username"
            button_text = "AUTHORIZE ADMIN ACCESS  🛡"

        self.identity_label = QLabel(identity_label)
        self.identity_label.setObjectName("fieldLabel")
        form_layout.addWidget(self.identity_label)

        self.identity = QLineEdit()
        self.identity.setObjectName("identityInput")
        self.identity.setPlaceholderText(identity_placeholder)
        self.identity.setFixedHeight(34)
        form_layout.addWidget(self.identity)

        self.hint = QLabel("Format: YYYY-XXXXX (e.g. 2024-12345)" if self.mode == "student" else " ")
        self.hint.setObjectName("fieldHint")
        form_layout.addWidget(self.hint)

        self.password_label = QLabel("PASSWORD")
        self.password_label.setObjectName("fieldLabel")
        form_layout.addWidget(self.password_label)

        password_row = QHBoxLayout()
        password_row.setSpacing(0)
        self.password = QLineEdit()
        self.password.setObjectName("passwordInput")
        self.password.setPlaceholderText("••••••••••••")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedHeight(34)
        password_row.addWidget(self.password)

        self.eye_button = QPushButton("👁")
        self.eye_button.setObjectName("eyeButton")
        self.eye_button.setFixedSize(34, 34)
        self.eye_button.setToolTip("Show or hide password")
        self.eye_button.clicked.connect(self.toggle_password_visibility)
        password_row.addWidget(self.eye_button)
        form_layout.addLayout(password_row)

        if self.mode == "student":
            options = QHBoxLayout()
            options.setContentsMargins(0, 4, 0, 4)
            self.remember = QCheckBox("Remember Student ID")
            self.remember.setObjectName("rememberCheck")
            options.addWidget(self.remember)
            options.addStretch(1)
            self.forgot = QPushButton("Forgot Password?")
            self.forgot.setObjectName("textButton")
            self.forgot.clicked.connect(self.forgot_password)
            options.addWidget(self.forgot)
            form_layout.addLayout(options)
        else:
            form_layout.addSpacing(10)

        self.login_button = QPushButton(button_text)
        self.login_button.setObjectName("loginButton")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setFixedHeight(36)
        self.login_button.clicked.connect(self.submit_login)
        form_layout.addWidget(self.login_button)

        self.status = QLabel("")
        self.status.setObjectName("statusMessage")
        self.status.setWordWrap(True)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.status)

        outer.addWidget(self.form, 0, Qt.AlignmentFlag.AlignTop)
        outer.addStretch(1)

        self.identity.returnPressed.connect(self.password.setFocus)
        self.password.returnPressed.connect(self.submit_login)

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        self.password.setEchoMode(
            QLineEdit.EchoMode.Normal if self.password_visible else QLineEdit.EchoMode.Password
        )

    def forgot_password(self):
        QMessageBox.information(
            self, "Password assistance",
            "Please contact the Integrated Library Services support desk to reset your password."
        )

    def submit_login(self):
        user_id = self.identity.text().strip()
        password = self.password.text()
        if not user_id or not password:
            self.status.setText("Please enter your ID and password.")
            self.status.setProperty("state", "error")
            self.status.style().unpolish(self.status)
            self.status.style().polish(self.status)
            self._shake_button()
            return

        # Demo-only response. Real authentication must be implemented server-side.
        role = "student/heatmap" if self.mode == "student" else "admin"
        self.status.setProperty("state", "success")
        self.status.setText(f"Form validated for {role}. Connect your approved authentication service here.")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def _shake_button(self):
        self.shake = QPropertyAnimation(self.login_button, b"pos", self)
        start_pos = self.login_button.pos()
        self.shake.setDuration(260)
        self.shake.setKeyValueAt(0.0, start_pos)
        self.shake.setKeyValueAt(0.2, start_pos + QPoint(-5, 0))
        self.shake.setKeyValueAt(0.4, start_pos + QPoint(5, 0))
        self.shake.setKeyValueAt(0.6, start_pos + QPoint(-3, 0))
        self.shake.setKeyValueAt(0.8, start_pos + QPoint(3, 0))
        self.shake.setKeyValueAt(1.0, start_pos)
        self.shake.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.shake.start()


class MainWindow(QMainWindow):
    """Main window composed of the header, mode selector, login pages, and footer."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TIP Integrated Library Services")
        self.setMinimumSize(760, 560)
        self.resize(1060, 680)
        self._animation = None
        self._build_ui()
        self._load_stylesheet()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Yellow institution banner.
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(62)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 5, 18, 5)
        header_layout.setSpacing(12)

        # Custom TIP logo image in the yellow header.
        logo = QLabel()
        logo.setObjectName("logoImage")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(47, 40)

        # Load the logo image from the project folder.
        logo_path = BASE_DIR / "tip_logo.png"
        logo_pixmap = QPixmap(str(logo_path))

        if not logo_pixmap.isNull():
            logo.setPixmap(
                logo_pixmap.scaled(
                    47,
                    40,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        else:
            logo.setText("TIP")
            logo.setToolTip("Place tip_logo.png beside main.py")

        header_layout.addWidget(logo)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        institute = QLabel("TECHNOLOGICAL INSTITUTE OF THE PHILIPPINES")
        institute.setObjectName("instituteTitle")
        subtitle = QLabel("Integrated Library Services")
        subtitle.setObjectName("instituteSubtitle")
        title_col.addWidget(institute)
        title_col.addWidget(subtitle)
        header_layout.addLayout(title_col)
        header_layout.addStretch(1)

        self.support_button = QPushButton("🎧 Support")
        self.support_button.setObjectName("supportButton")
        self.support_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.support_button.clicked.connect(self.show_support)
        header_layout.addWidget(self.support_button)
        root_layout.addWidget(header)

        # Main white area.
        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 38, 20, 24)
        content_layout.setSpacing(0)
        content_layout.addStretch(1)

        self.mode_bar = QFrame()
        self.mode_bar.setObjectName("modeBar")
        self.mode_bar.setFixedSize(330, 40)
        mode_layout = QHBoxLayout(self.mode_bar)
        mode_layout.setContentsMargins(4, 4, 4, 4)
        mode_layout.setSpacing(4)

        self.student_tab = QPushButton("🔥 Space Heatmap")
        self.student_tab.setObjectName("modeButton")
        self.student_tab.setProperty("active", True)
        self.library_tab = QPushButton("📖 Library")
        self.library_tab.setObjectName("modeButton")
        self.library_tab.setProperty("active", False)
        self.admin_tab = QPushButton("👤 Admin")
        self.admin_tab.setObjectName("modeButton")
        self.admin_tab.setProperty("active", False)
        for button in (self.student_tab, self.library_tab, self.admin_tab):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            mode_layout.addWidget(button)
        self.student_tab.clicked.connect(lambda: self.switch_mode("student"))
        self.library_tab.clicked.connect(lambda: self.switch_mode("library"))
        self.admin_tab.clicked.connect(lambda: self.switch_mode("admin"))
        content_layout.addWidget(self.mode_bar, 0, Qt.AlignmentFlag.AlignHCenter)
        content_layout.addSpacing(22)

        self.pages = QStackedWidget()
        self.pages.setObjectName("loginPages")
        self.student_page = LoginForm("student")
        self.library_page = LibraryLoginForm()
        self.admin_page = LoginForm("admin")
        self.pages.addWidget(self.student_page)
        self.pages.addWidget(self.library_page)
        self.pages.addWidget(self.admin_page)
        self.pages.setMaximumWidth(330)
        content_layout.addWidget(self.pages, 0, Qt.AlignmentFlag.AlignHCenter)
        content_layout.addStretch(2)
        root_layout.addWidget(content, 1)

        footer = QLabel("© 2026 Technological Institute of the Philippines. All Rights Reserved.")
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setFixedHeight(28)
        root_layout.addWidget(footer)

    def _load_stylesheet(self):
        qss_path = BASE_DIR / "style.qss"
        try:
            self.setStyleSheet(qss_path.read_text(encoding="utf-8"))
        except OSError:
            self.setStyleSheet(self._fallback_stylesheet())

    def _fallback_stylesheet(self):
        return "QMainWindow, QWidget { background: white; color: #242424; } QPushButton { padding: 8px; }"

    def switch_mode(self, mode: str):
        page_map = {"student": 0, "library": 1, "admin": 2}
        
        index = page_map[mode]
        if self.pages.currentIndex() == index:
            return
        
        self.student_tab.setProperty("active", mode == "student")
        self.library_tab.setProperty("active", mode == "library")
        self.admin_tab.setProperty("active", mode == "admin")

        for button in (
            self.student_tab,
            self.library_tab,
            self.admin_tab
        ):
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

        self.pages.setCurrentIndex(index)
        effect = QGraphicsOpacityEffect(self.pages.currentWidget())
        self.pages.currentWidget().setGraphicsEffect(effect)
        self._animation = QPropertyAnimation(effect, b"opacity", self)

        self._animation.setDuration(230)
        self._animation.setStartValue(0.15)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(
        QEasingCurve.Type.OutCubic
    )

        self._animation.start()

    def show_support(self):
        QMessageBox.information(
            self, "Integrated Library Services Support",
            "For account access or password assistance, contact the library support desk.\n\n"
            "This prototype does not send support requests or connect to a live service."
        )

    def save_debug_log(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save UI Log", str(BASE_DIR / "logs" / "login-ui-log.txt"), "Text Files (*.txt)"
        )
        if path:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8") as file:
                file.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] UI log exported.\n")
            QMessageBox.information(self, "Saved", "The UI log was saved successfully.")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TIP Integrated Library Services")
    app.setFont(QFont("Arial", 9))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()