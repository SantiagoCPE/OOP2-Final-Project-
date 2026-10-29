from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
                            QHBoxLayout, QComboBox)


class LibraryLoginForm(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.password_visible = False
        self.build_ui()

    def build_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        branch_label = QLabel("LIBRARY BRANCH / SECTION")
        branch_label.setObjectName("fieldLabel")
        layout.addWidget(branch_label)

        self.branch = QComboBox()
        self.branch.setObjectName("libraryBranch")
        self.branch.setFixedHeight(34)

        self.branch.setPlaceholderText("Select Campus Library")
        self.branch.addItem("Library 1 (Bldg 1)")
        self.branch.addItem("Library 2 (Bldg 8)")
        self.branch.setCurrentIndex(-1)

        layout.addWidget(self.branch)

        member_label = QLabel("LIBRARY MEMBER / STAFF ID")
        member_label.setObjectName("fieldLabel")
        layout.addWidget(member_label)

        self.member_id = QLineEdit()
        self.member_id.setObjectName("identityInput")
        self.member_id.setPlaceholderText("e.g. LIB-2024-883")
        self.member_id.setFixedHeight(34)

        layout.addWidget(self.member_id)

        password_label = QLabel("PASSWORD")
        password_label.setObjectName("fieldLabel")
        layout.addWidget(password_label)

        password_row = QHBoxLayout()
        password_row.setSpacing(0)

        self.password = QLineEdit()
        self.password.setObjectName("passwordInput")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedHeight(34)

        password_row.addWidget(self.password)

        self.eye_button = QPushButton("👁")
        self.eye_button.setObjectName("eyeButton")
        self.eye_button.setFixedSize(34, 34)
        self.eye_button.clicked.connect(
            self.toggle_password_visibility
        )

        password_row.addWidget(self.eye_button)

        layout.addLayout(password_row)

        layout.addSpacing(10)

        self.login_button = QPushButton(
            "SIGN IN TO LIBRARY SERVICES →"
        )

        self.login_button.setObjectName("loginButton")
        self.login_button.setFixedHeight(40)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)
        self.status = QLabel("")
        self.status.setObjectName("statusMessage")
        self.status.setWordWrap(True)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.status)

        layout.addStretch()
    
    def login(self):
        self.status.setText("Please enter your ID and password")
        self.status.setProperty("state", "error")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)
        self.shake_button()

    def toggle_password_visibility(self):

        self.password_visible = not self.password_visible

        self.password.setEchoMode(
            QLineEdit.EchoMode.Normal
            if self.password_visible
            else QLineEdit.EchoMode.Password
        )
    def shake_button(self):

        self.shake = QPropertyAnimation(self.login_button, b"pos", self)
        start_pos = self.login_button.pos()
        self.shake.setDuration(350)
        self.shake.setKeyValueAt(0.0, start_pos)
        self.shake.setKeyValueAt(0.2, start_pos + QPoint(-8, 0))
        self.shake.setKeyValueAt(0.4, start_pos + QPoint(8, 0))
        self.shake.setKeyValueAt(0.6, start_pos + QPoint(-6, 0))
        self.shake.setKeyValueAt(0.8, start_pos + QPoint(6, 0))
        self.shake.setKeyValueAt(1.0, start_pos)
        self.shake.start()