from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton)

from core import auth
from ui.common import STUDENT_NUMBER_RULE, confirm_student_number, limit_to_student_number


def _shell(page: QWidget, title: str, subtitle: str, width: int = 400):
    """Centered column used by every selection/login page. Returns (title_label, sub_label, column_layout)."""
    page.setObjectName("pageBg")
    outer = QVBoxLayout(page)
    outer.addStretch(1)
    row = QHBoxLayout()
    row.addStretch(1)
    column_widget = QWidget()
    column_widget.setFixedWidth(width)
    column = QVBoxLayout(column_widget)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(10)
    t = QLabel(title); t.setObjectName("pageTitle"); t.setAlignment(Qt.AlignmentFlag.AlignCenter)
    s = QLabel(subtitle); s.setObjectName("pageSub"); s.setAlignment(Qt.AlignmentFlag.AlignCenter)
    s.setWordWrap(True)
    column.addWidget(t); column.addWidget(s); column.addSpacing(14)
    row.addWidget(column_widget); row.addStretch(1)
    outer.addLayout(row)
    outer.addStretch(2)
    return t, s, column


def _choice_button(text: str) -> QPushButton:
    b = QPushButton(text)
    b.setObjectName("choiceButton")
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b


def _back_button(text="← Back") -> QPushButton:
    b = QPushButton(text)
    b.setObjectName("linkButton")
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b


class RolePage(QWidget):
    student_chosen = pyqtSignal()
    admin_chosen = pyqtSignal()

    def __init__(self):
        super().__init__()
        _, _, col = _shell(self, "Welcome", "Choose how you are using the Library Space Heat Map.")
        student = _choice_button("Student\nView, reserve")
        admin = _choice_button("Admin\nLibrarian, entrance")
        student.clicked.connect(self.student_chosen.emit)
        admin.clicked.connect(self.admin_chosen.emit)
        col.addWidget(student); col.addWidget(admin)


class AdminTypePage(QWidget):
    librarian_chosen = pyqtSignal()
    entrance_chosen = pyqtSignal()
    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        _, _, col = _shell(self, "Admin Access", "Which access do you need?")
        lib = _choice_button("Librarian Access\nView, remove reservations")
        ent = _choice_button("Entrance Access\nLog in, log out")
        lib.clicked.connect(self.librarian_chosen.emit)
        ent.clicked.connect(self.entrance_chosen.emit)
        back = _back_button(); back.clicked.connect(self.back.emit)
        col.addWidget(lib); col.addWidget(ent); col.addSpacing(6); col.addWidget(back)


class StudentLoginPage(QWidget):
    logged_in = pyqtSignal(str)
    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        _, _, col = _shell(self, "Student Access", "Enter your student number to open the heat map.")
        lbl = QLabel("STUDENT NUMBER"); lbl.setObjectName("fieldLabel")
        self.number = QLineEdit(); self.number.setObjectName("field")
        self.number.setPlaceholderText("(26)34567"); limit_to_student_number(self.number)
        hint = QLabel("7 digits, numbers only (e.g. (26)34567)"); hint.setObjectName("fieldHint")
        self.status = QLabel(""); self.status.setObjectName("statusError")
        self.status.setWordWrap(True); self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        go = QPushButton("ACCESS SPACE HEATMAP  →"); go.setObjectName("primaryButton")
        go.setCursor(Qt.CursorShape.PointingHandCursor)
        back = _back_button(); back.clicked.connect(self.back.emit)
        col.addWidget(lbl); col.addWidget(self.number); col.addWidget(hint)
        col.addSpacing(6); col.addWidget(go); col.addWidget(self.status); col.addWidget(back)
        go.clicked.connect(self._submit)
        self.number.returnPressed.connect(self._submit)

    def reset(self):
        self.number.clear(); self.status.clear(); self.number.setFocus()

    def _submit(self):
        value = self.number.text().strip()
        if not auth.is_valid_student_number(value):
            self.status.setText(STUDENT_NUMBER_RULE)
            return
        self.status.clear()
        if confirm_student_number(self, value, "This number will be used for your reservations."):
            self.logged_in.emit(value)
        else:
            self.number.setFocus(); self.number.selectAll()


class AdminLoginPage(QWidget):
    logged_in = pyqtSignal(str, str)   # kind, username
    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.kind = "librarian"
        self.title_label, self.sub_label, col = _shell(self, "Admin Login", "")
        ulbl = QLabel("USERNAME"); ulbl.setObjectName("fieldLabel")
        self.username = QLineEdit(); self.username.setObjectName("field")
        self.username.setPlaceholderText("username")
        plbl = QLabel("PASSWORD"); plbl.setObjectName("fieldLabel")
        prow = QHBoxLayout(); prow.setSpacing(0)
        self.password = QLineEdit(); self.password.setObjectName("field")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("••••••••")
        eye = QPushButton("👁"); eye.setObjectName("eyeButton"); eye.setFixedWidth(40)
        eye.setCursor(Qt.CursorShape.PointingHandCursor)
        eye.clicked.connect(self._toggle_password)
        prow.addWidget(self.password); prow.addWidget(eye)
        self.status = QLabel(""); self.status.setObjectName("statusError")
        self.status.setWordWrap(True); self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        go = QPushButton("SIGN IN  →"); go.setObjectName("primaryButton")
        go.setCursor(Qt.CursorShape.PointingHandCursor)
        back = _back_button(); back.clicked.connect(self.back.emit)
        col.addWidget(ulbl); col.addWidget(self.username)
        col.addWidget(plbl); col.addLayout(prow)
        col.addSpacing(6); col.addWidget(go); col.addWidget(self.status); col.addWidget(back)
        go.clicked.connect(self._submit)
        self.username.returnPressed.connect(self.password.setFocus)
        self.password.returnPressed.connect(self._submit)

    def set_kind(self, kind: str):
        self.kind = kind
        label = auth.ADMIN_LABELS[kind]
        self.title_label.setText(label)
        self.sub_label.setText("Sign in with your admin username and password.")
        self.username.clear(); self.password.clear(); self.status.clear()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.username.setFocus()

    def _toggle_password(self):
        hidden = self.password.echoMode() == QLineEdit.EchoMode.Password
        self.password.setEchoMode(QLineEdit.EchoMode.Normal if hidden else QLineEdit.EchoMode.Password)

    def _submit(self):
        user, pw = self.username.text().strip(), self.password.text()
        if not user or not pw:
            self.status.setText("Please enter your username and password."); return
        if not auth.verify_admin(self.kind, user, pw):
            self.status.setText("Incorrect username or password."); self.password.clear(); return
        self.status.clear()
        self.logged_in.emit(self.kind, user)
        self.password.clear()
