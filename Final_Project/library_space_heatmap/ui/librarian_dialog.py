from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
                             QPushButton, QVBoxLayout)
from PyQt6.QtGui import QColor

from core.seat_manager import MAX_RESERVATION_MINUTES, SeatManager
from ui.common import ask_yes_no, notify
from ui.theme import DIALOG_STYLES


class LibrarianReservationDialog(QDialog):
    """Shows who reserved a yellow chair and when, and lets the librarian remove reservations."""

    def __init__(self, seat_id, seat_manager, on_change, parent=None):
        super().__init__(parent)
        self.seat_id, self.seat_manager, self.on_change = seat_id, seat_manager, on_change
        self.setWindowTitle("Librarian — Reservation Details")
        self.setFixedWidth(500)
        self.setModal(True)
        self.setStyleSheet(DIALOG_STYLES)
        lay = QVBoxLayout(self); lay.setContentsMargins(24, 24, 24, 22); lay.setSpacing(12)
        title = QLabel("Reservation Details"); title.setObjectName("title")
        sub = QLabel(f"Seat: {seat_id}  •  Reserved (yellow)"); sub.setObjectName("sub")
        div = QFrame(); div.setFrameShape(QFrame.Shape.HLine); div.setStyleSheet("color:#e3dcc9")
        rule = QLabel(f"Reservations are limited to {MAX_RESERVATION_MINUTES} minutes. "
                      "Remove any that are over the limit or expired.")
        rule.setWordWrap(True); rule.setObjectName("sub")
        self.list = QListWidget(); self.list.setMinimumHeight(170)
        self.list.currentRowChanged.connect(self._show_detail)
        self.detail = QLabel(""); self.detail.setWordWrap(True)
        self.detail.setStyleSheet("background:#fff6d5;border:1px solid #f0e4b8;border-radius:8px;padding:10px;")
        row = QHBoxLayout()
        close = QPushButton("Close"); close.setObjectName("cancel"); close.clicked.connect(self.accept)
        sel = QPushButton("Remove Selected"); sel.setObjectName("secondary"); sel.clicked.connect(self._remove_selected)
        allb = QPushButton("Remove All"); allb.setObjectName("danger"); allb.clicked.connect(self._remove_all)
        row.addWidget(close); row.addWidget(sel); row.addWidget(allb)
        for w in (title, sub, div, rule, self.list, self.detail):
            lay.addWidget(w)
        lay.addLayout(row)
        self._reload()

    def _reload(self):
        self.list.clear()
        self._items = self.seat_manager.reservations_for(self.seat_id)
        for r in self._items:
            problem = SeatManager.reservation_problem(r)
            text = f"{r['student']}   •   {r['date']}   {r['start']:%I:%M %p} – {r['end']:%I:%M %p}"
            if problem:
                text += f"   ⚠ {problem}"
            item = QListWidgetItem(text)
            if problem:
                item.setForeground(QColor("#c4171d"))
            self.list.addItem(item)
        if self._items:
            self.list.setCurrentRow(0)
        else:
            self.accept()   # chair is no longer reserved

    def _show_detail(self, idx):
        if not 0 <= idx < len(getattr(self, "_items", [])):
            self.detail.setText(""); return
        r = self._items[idx]
        mins = SeatManager.reservation_minutes(r)
        problem = SeatManager.reservation_problem(r)
        text = (f"<b>Student number:</b> {r['student']}<br>"
                f"<b>Date:</b> {r['date']}<br>"
                f"<b>Time reserved:</b> {r['start']:%I:%M %p} – {r['end']:%I:%M %p} ({mins} min)")
        if problem:
            text += f"<br><b style='color:#c4171d'>⚠ {problem} — should be removed.</b>"
        self.detail.setText(text)

    def _remove_selected(self):
        idx = self.list.currentRow()
        if idx < 0:
            notify(self, "Select one", "Please select a reservation first.", warning=True); return
        r = self._items[idx]
        if ask_yes_no(self, "Remove reservation", f"Remove the reservation of student {r['student']}?"):
            ok, msg = self.seat_manager.remove_reservation(self.seat_id, idx)
            if not ok: notify(self, "Seat Access", msg, warning=True)
            self.on_change(); self._reload()

    def _remove_all(self):
        if ask_yes_no(self, "Remove all", f"Remove ALL reservations on seat {self.seat_id}?"):
            self.seat_manager.clear_reservations(self.seat_id)
            self.on_change(); self.accept()


FLOOR_NAMES = {"first": "First Floor", "right": "Second Floor (Right Wing)", "left": "Second Floor (Left Wing)"}


class LibrarianOccupantDialog(QDialog):
    """Details of the student logged into a red chair, with a button to log them out."""

    def __init__(self, seat_id, seat_manager, on_change, parent=None):
        super().__init__(parent)
        self.seat_id, self.seat_manager, self.on_change = seat_id, seat_manager, on_change
        self.setWindowTitle("Librarian — Occupant Details")
        self.setFixedWidth(430)
        self.setModal(True)
        self.setStyleSheet(DIALOG_STYLES)
        student = seat_manager.owner(seat_id)
        since = seat_manager.owner_since(seat_id)
        lay = QVBoxLayout(self); lay.setContentsMargins(24, 24, 24, 22); lay.setSpacing(12)
        title = QLabel("Occupant Details"); title.setObjectName("title")
        sub = QLabel(f"Seat: {seat_id}  •  Occupied (red)"); sub.setObjectName("sub")
        div = QFrame(); div.setFrameShape(QFrame.Shape.HLine); div.setStyleSheet("color:#e3dcc9")
        floor = FLOOR_NAMES.get(seat_id.split("-")[0], "")
        text = f"<b>Student number:</b> {student}<br><b>Floor:</b> {floor}<br>"
        if since:
            mins = max(0, int((datetime.now() - since).total_seconds() // 60))
            text += (f"<b>Logged in at:</b> {since:%I:%M %p, %Y-%m-%d}<br>"
                     f"<b>Time seated:</b> {mins // 60} hr {mins % 60} min")
        else:
            text += "<b>Logged in at:</b> not recorded"
        upcoming = len(seat_manager.reservations_for(seat_id))
        if upcoming:
            text += f"<br><b>Upcoming reservations on this seat:</b> {upcoming}"
        detail = QLabel(text)
        detail.setStyleSheet("background:#fff6d5;border:1px solid #f0e4b8;border-radius:8px;padding:12px;")
        row = QHBoxLayout()
        close = QPushButton("Close"); close.setObjectName("cancel"); close.clicked.connect(self.accept)
        remove = QPushButton("Log Out Student"); remove.setObjectName("danger"); remove.clicked.connect(self._remove)
        row.addWidget(close); row.addWidget(remove)
        for w in (title, sub, div, detail):
            lay.addWidget(w)
        lay.addLayout(row)

    def _remove(self):
        student = self.seat_manager.owner(self.seat_id)
        if not ask_yes_no(self, "Log out student", f"Log student {student} out of seat {self.seat_id}?",
                          "The chair will turn green for everyone."):
            return
        ok, msg = self.seat_manager.force_release(self.seat_id)
        notify(self, "Done" if ok else "Seat Access", msg, warning=not ok)
        self.on_change(); self.accept()
