from datetime import datetime

from PyQt6.QtCore import QDate, QTime
from PyQt6.QtGui import QColor, QTextCharFormat
from PyQt6.QtWidgets import (QCalendarWidget, QDialog, QFrame, QHBoxLayout, QLabel, QPushButton,
                             QSpinBox, QStackedWidget, QTimeEdit, QVBoxLayout, QWidget)

from ui.common import notify
from core.seat_manager import MAX_RESERVATION_MINUTES
from ui.theme import DIALOG_STYLES


class CustomCalendarWidget(QCalendarWidget):
    """Greys out dates that already hold the maximum number of reservations."""

    def __init__(self, seat_manager, parent=None):
        super().__init__(parent)
        self.seat_manager = seat_manager
        self.setMinimumDate(QDate.currentDate())
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#e0e0e0")); fmt.setForeground(QColor("#a0a0a0"))
        today = QDate.currentDate()
        for i in range(60):
            d = today.addDays(i)
            if seat_manager.is_date_overbooked(d.toString("yyyy-MM-dd")):
                self.setDateTextFormat(d, fmt)


class SeatReservationDialog(QDialog):
    """Student dialog. The student number was confirmed at login, so it is never re-typed here."""

    def __init__(self, seat_id, seat_manager, student_number, parent=None):
        super().__init__(parent)
        self.seat_id, self.seat_manager, self.student_number = seat_id, seat_manager, student_number
        self.status = seat_manager.status(seat_id)
        self.setWindowTitle("Library Seat Access")
        self.setFixedWidth(400)
        self.setModal(True)
        self.setStyleSheet(DIALOG_STYLES)

        layout = QVBoxLayout(self); layout.setContentsMargins(24, 24, 24, 22); layout.setSpacing(12)
        title = QLabel("Library Seat Access"); title.setObjectName("title")
        sub = QLabel(f"Seat: {seat_id}  •  Status: {self.status.title()}"); sub.setObjectName("sub")
        who = QLabel(f"Signed in as student {student_number}"); who.setObjectName("ok")
        div = QFrame(); div.setFrameShape(QFrame.Shape.HLine); div.setStyleSheet("color:#e3dcc9")
        layout.addWidget(title); layout.addWidget(sub); layout.addWidget(who); layout.addWidget(div)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_action_page())
        self.pages.addWidget(self._build_schedule_page())
        layout.addWidget(self.pages)

    def _btn(self, text, slot, name=None):
        b = QPushButton(text)
        if name: b.setObjectName(name)
        b.clicked.connect(slot)
        return b

    def _build_action_page(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(10)
        note = QLabel(); note.setWordWrap(True); note.setObjectName("prompt")
        lay.addWidget(note)
        if self.status == "occupied":
            note.setText("This seat is currently occupied.")
        else:
            if self.status == "reserved":
                note.setText("This seat has a reservation. You can reserve a different time slot.")
            else:
                note.setText("This seat is available to reserve.")
            lay.addWidget(self._btn("Reserve", lambda: self.pages.setCurrentIndex(1)))
        lay.addWidget(self._btn("Close", self.reject, "cancel"))
        return page

    def _build_schedule_page(self):
        page = QWidget(); lay = QVBoxLayout(page); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(10)
        lay.addWidget(QLabel(f"Select Reservation Date (max {MAX_RESERVATION_MINUTES} minutes):"))
        self.calendar = CustomCalendarWidget(self.seat_manager)
        lay.addWidget(self.calendar)
        row = QHBoxLayout(); row.setSpacing(6)
        self.time_edit = QTimeEdit(); self.time_edit.setDisplayFormat("hh:mm AP")
        self.time_edit.setTime(QTime.currentTime())
        self.duration = QSpinBox(); self.duration.setRange(5, MAX_RESERVATION_MINUTES); self.duration.setSingleStep(5)
        self.duration.setValue(MAX_RESERVATION_MINUTES); self.duration.setSuffix(' min')
        row.addWidget(QLabel("Start:")); row.addWidget(self.time_edit); row.addSpacing(8)
        row.addWidget(QLabel("Length:")); row.addWidget(self.duration)
        lay.addLayout(row)
        btns = QHBoxLayout()
        btns.addWidget(self._btn("Back", lambda: self.pages.setCurrentIndex(0), "cancel"))
        btns.addWidget(self._btn("Confirm Schedule", self._confirm_reservation))
        lay.addLayout(btns)
        return page

    def _finish(self, ok, msg):
        if ok:
            notify(self, "Done", msg); self.accept()
        else:
            notify(self, "Seat Access", msg, warning=True)

    def _confirm_reservation(self):
        qd, t = self.calendar.selectedDate(), self.time_edit.time()
        start = datetime(qd.year(), qd.month(), qd.day(), t.hour(), t.minute())
        self._finish(*self.seat_manager.reserve(
            self.seat_id, self.student_number, qd.toString("yyyy-MM-dd"), start, self.duration.value()))
