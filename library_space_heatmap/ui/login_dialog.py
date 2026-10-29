from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame

class SeatLoginDialog(QDialog):
    def __init__(self, seat_id, status, parent=None):
        super().__init__(parent)
        self.status = status
        self.setWindowTitle("Library Seat Access")
        self.setFixedWidth(380)
        self.setModal(True)
        self.setStyleSheet("""
            QDialog { background: #fffdf5; }
            QLabel#title { color: #171717; font-size: 20px; font-weight: 700; }
            QLabel#sub { color: #5b5b5b; font-size: 12px; }
            QLineEdit { border: 1px solid #cfc8b4; border-radius: 7px; padding: 11px; background: white; font-size: 14px; }
            QPushButton { background: #ffcc00; border: 1px solid #e4b700; border-radius: 7px; padding: 10px 14px; font-weight: 700; }
            QPushButton#cancel { background: white; border: 1px solid #d7d0bd; }
        """)
        layout = QVBoxLayout(self); layout.setContentsMargins(24,24,24,22); layout.setSpacing(12)
        title = QLabel("Library Seat Access"); title.setObjectName("title")
        subtitle = QLabel(f"Seat: {seat_id}  •  Status: {'Occupied' if status == 'occupied' else 'Available'}")
        subtitle.setObjectName("sub")
        layout.addWidget(title); layout.addWidget(subtitle)
        divider = QFrame(); divider.setFrameShape(QFrame.Shape.HLine); divider.setStyleSheet("color:#e3dcc9")
        layout.addWidget(divider)
        prompt = "Enter the same student number to log out of this seat." if status == "occupied" else "Enter your student number to occupy this seat."
        layout.addWidget(QLabel(prompt))
        self.student_input = QLineEdit(); self.student_input.setPlaceholderText("Student number")
        self.student_input.setClearButtonEnabled(True)
        self.student_input.returnPressed.connect(self.accept)
        layout.addWidget(self.student_input)
        buttons = QHBoxLayout()
        cancel = QPushButton("Cancel"); cancel.setObjectName("cancel"); cancel.clicked.connect(self.reject)
        action = QPushButton("Log Out" if status == "occupied" else "Log In")
        action.clicked.connect(self.accept)
        buttons.addWidget(cancel); buttons.addWidget(action); layout.addLayout(buttons)
        self.student_input.setFocus()

    def student_number(self):
        return self.student_input.text()
