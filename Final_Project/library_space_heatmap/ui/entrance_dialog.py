from PyQt6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from core import auth
from ui.common import STUDENT_NUMBER_RULE, confirm_student_number, limit_to_student_number, notify
from ui.theme import DIALOG_STYLES


class EntranceSeatDialog(QDialog):
    """Entrance staff log a student in/out of a chair. The number is confirmed before anything happens."""

    def __init__(self, seat_id, seat_manager, parent=None):
        super().__init__(parent)
        self.seat_id, self.seat_manager = seat_id, seat_manager
        self.status = seat_manager.status(seat_id)
        self.setWindowTitle("Entrance — Seat Access")
        self.setFixedWidth(390)
        self.setModal(True)
        self.setStyleSheet(DIALOG_STYLES)
        lay = QVBoxLayout(self); lay.setContentsMargins(24, 24, 24, 22); lay.setSpacing(12)
        title = QLabel("Entrance Seat Access"); title.setObjectName("title")
        sub = QLabel(f"Seat: {seat_id}  •  Status: {self.status.title()}"); sub.setObjectName("sub")
        div = QFrame(); div.setFrameShape(QFrame.Shape.HLine); div.setStyleSheet("color:#e3dcc9")
        lay.addWidget(title); lay.addWidget(sub); lay.addWidget(div)

        if self.status == "occupied":
            prompt, action_text = "Enter the same student number that logged into this seat to log out:", "Log Out"
        elif self.status == "reserved":
            prompt, action_text = "Reserved seat. Enter the reservation holder's student number to log in:", "Log In"
        else:
            prompt, action_text = "Enter the student number to log in to this seat:", "Log In"
        p = QLabel(prompt); p.setObjectName("prompt"); p.setWordWrap(True)
        self.number = QLineEdit(); self.number.setPlaceholderText("Student number (7 digits)"); limit_to_student_number(self.number)
        self.number.setClearButtonEnabled(True)
        self.number.returnPressed.connect(self._submit)
        lay.addWidget(p); lay.addWidget(self.number)
        row = QHBoxLayout()
        cancel = QPushButton("Cancel"); cancel.setObjectName("cancel"); cancel.clicked.connect(self.reject)
        action = QPushButton(action_text); action.clicked.connect(self._submit)
        row.addWidget(cancel); row.addWidget(action); lay.addLayout(row)
        self.number.setFocus()

    def _submit(self):
        value = self.number.text().strip()
        if not auth.is_valid_student_number(value):
            notify(self, "Invalid student number", STUDENT_NUMBER_RULE, warning=True)
            return
        if not confirm_student_number(self, value):
            self.number.setFocus(); self.number.selectAll(); return
        if self.status == "occupied":
            ok, msg = self.seat_manager.release(self.seat_id, value)
        else:
            ok, msg = self.seat_manager.occupy(self.seat_id, value)
        if ok:
            notify(self, "Done", msg); self.accept()
        else:
            notify(self, "Seat Access", msg, warning=True)
