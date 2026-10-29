import json
import os

from PyQt6.QtCore import QEasingCurve, QPointF, QRect, QRectF, Qt, QTimer, QVariantAnimation
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy,
                             QVBoxLayout, QWidget)

from ui.common import notify
from ui.entrance_dialog import EntranceSeatDialog
from ui.librarian_dialog import LibrarianOccupantDialog, LibrarianReservationDialog
from ui.reservation_dialog import SeatReservationDialog

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Image folder: "images" (current name); falls back to the old "assets" name if present.
ASSETS = next((os.path.join(ROOT, n) for n in ("images", "assets") if os.path.isdir(os.path.join(ROOT, n))),
              os.path.join(ROOT, "images"))

FLOORS = [
    ("first", "First Floor", ""),
    ("right", "Second Floor", "Right Wing"),
    ("left", "Second Floor", "Left Wing"),
]
# Region of the reference screenshots that holds the floor plan (chair_positions.json uses screenshot coordinates).
PLAN_CROP = {
    "first": QRect(152, 88, 886, 497),
    "right": QRect(151, 88, 885, 496),
    "left": QRect(151, 88, 889, 496),
}
PLAN_IMAGE = {"first": "plan_first.png", "right": "plan_right.png", "left": "plan_left.png"}

COLORS = {"occupied": "#ff575d", "reserved": "#ffcc00", "available": "#b8ff72"}


class SeatButton(QPushButton):
    def __init__(self, seat_id, side_view, callback, parent=None):
        super().__init__(parent)
        self.seat_id, self.side_view, self.seat_status = seat_id, side_view, "available"
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda: callback(self.seat_id))
        self.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0; }")
        self.setAccessibleName(f"Library seat {seat_id}")
        self.update_status("available", force=True)

    def update_status(self, status, force=False):
        if status == self.seat_status and not force:
            return
        self.seat_status = status
        self.setToolTip(f"Seat {self.seat_id} — {status.title()}")
        self.update()

    def set_clickable(self, clickable: bool):
        self.setCursor(Qt.CursorShape.PointingHandCursor if clickable else Qt.CursorShape.ArrowCursor)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        r = QRectF(self.rect()).adjusted(1.2, 1.2, -1.2, -1.2)
        # White backing hides any faint leftovers of the original chair drawing.
        p.fillRect(self.rect().adjusted(0, 0, 0, 0), QColor("#ffffff"))
        pen = QPen(QColor("#101010"))
        pen.setWidthF(max(1.1, min(2.0, min(r.width(), r.height()) * .075)))
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(QColor(COLORS[self.seat_status]))

        if self.side_view and r.width() > r.height() * .70:
            path = QPainterPath()
            path.moveTo(r.left() + r.width() * .22, r.top() + r.height() * .12)
            path.cubicTo(r.left() + r.width() * .06, r.top() + r.height() * .08,
                         r.left() + r.width() * .06, r.bottom() - r.height() * .08,
                         r.left() + r.width() * .22, r.bottom() - r.height() * .10)
            path.cubicTo(r.left() + r.width() * .30, r.bottom() - r.height() * .14,
                         r.left() + r.width() * .29, r.top() + r.height() * .14,
                         r.left() + r.width() * .22, r.top() + r.height() * .12)
            p.drawPath(path)
            p.drawRoundedRect(QRectF(r.left() + r.width() * .25, r.top() + r.height() * .22,
                                     r.width() * .68, r.height() * .56), r.width() * .09, r.height() * .09)
            sw, sh = r.width() * .40, max(2, r.height() * .12)
            sx = r.left() + r.width() * .49
            p.drawRoundedRect(QRectF(sx, r.top() + r.height() * .04, sw, sh), 2, 2)
            p.drawRoundedRect(QRectF(sx, r.bottom() - sh - r.height() * .04, sw, sh), 2, 2)
        else:
            band_h = max(2.4, r.height() * .20)
            body = QRectF(r.left(), r.top(), r.width(), r.height() - band_h * .52)
            radius = min(r.width() * .23, r.height() * .28)
            p.drawRoundedRect(body, radius, radius)
            p.drawRect(QRectF(r.left(), r.bottom() - band_h, r.width(), band_h))
        if self.underMouse():
            p.setBrush(Qt.BrushStyle.NoBrush)
            hp = QPen(QColor("#e5ae00")); hp.setWidthF(1.6); p.setPen(hp)
            p.drawRoundedRect(r.adjusted(-.5, -.5, .5, .5), 3, 3)
        p.end()


class LegendSymbol(QWidget):
    def __init__(self, kind="chair", color="#b8ff72", parent=None):
        super().__init__(parent)
        self.kind, self.color = kind, QColor(color)
        self.setFixedSize(28 if kind == "chair" else 54, 24)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(QPen(QColor("#111111"), 1.25))
        if self.kind == "desk":
            p.setBrush(QColor("#ffffff")); p.drawRect(QRectF(1.5, 3, self.width() - 3, self.height() - 6))
        elif self.kind == "side":
            p.setBrush(self.color)
            p.drawRoundedRect(QRectF(1, 4, 6, 16), 2, 2); p.drawRoundedRect(QRectF(7, 7, 17, 10), 2, 2)
            p.drawRoundedRect(QRectF(10, 1.5, 11, 4), 1.5, 1.5); p.drawRoundedRect(QRectF(10, 18, 11, 4), 1.5, 1.5)
        else:
            p.setBrush(self.color)
            p.drawRoundedRect(QRectF(3, 2, 21, 18), 4, 4); p.drawRect(QRectF(3, 15, 21, 4))
        p.end()


class FloorPlanWidget(QWidget):
    """Floor-plan image (aspect ratio preserved) with live seat buttons placed on top."""

    def __init__(self, floor_key, seat_manager, seat_callback, parent=None):
        super().__init__(parent)
        self.floor_key, self.seat_manager = floor_key, seat_manager
        self.setMinimumSize(540, 360)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.plan = QPixmap(os.path.join(ASSETS, PLAN_IMAGE[floor_key]))
        self.crop = PLAN_CROP[floor_key]
        self.plan_w, self.plan_h = self.crop.width(), self.crop.height()
        with open(os.path.join(ROOT, "chair_positions.json"), encoding="utf-8") as f:
            positions = json.load(f)[floor_key]
        self.buttons = []
        for i, box in enumerate(positions, start=1):
            seat_id = f"{floor_key}-{i:03d}"
            b = SeatButton(seat_id, box[2] >= 25 and box[3] >= 25, seat_callback, self)
            b._box = box
            b.update_status(seat_manager.status(seat_id))
            self.buttons.append(b)
        self._scale, self._ox, self._oy = 1.0, 0.0, 0.0
        self.layout_buttons()

    def _fit(self):
        s = min(self.width() / self.plan_w, self.height() / self.plan_h)
        self._scale = s
        self._ox = (self.width() - self.plan_w * s) / 2
        self._oy = (self.height() - self.plan_h * s) / 2

    def layout_buttons(self):
        self._fit()
        s = self._scale
        for b in self.buttons:
            x, y, w, h = b._box
            b.setGeometry(round(self._ox + (x - self.crop.x()) * s), round(self._oy + (y - self.crop.y()) * s),
                          max(9, round(w * s)), max(9, round(h * s)))

    def resizeEvent(self, event):
        self.layout_buttons()
        super().resizeEvent(event)

    def refresh_seats(self):
        for b in self.buttons:
            b.update_status(self.seat_manager.status(b.seat_id))

    def set_clickable_rule(self, rule):
        """rule(status) -> bool decides which seats show a pointer cursor."""
        for b in self.buttons:
            b.set_clickable(rule(b.seat_status))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        p.fillRect(self.rect(), QColor("#ffffff"))
        if not self.plan.isNull():
            target = QRectF(self._ox, self._oy, self.plan_w * self._scale, self.plan_h * self._scale)
            p.drawPixmap(target, self.plan, QRectF(self.plan.rect()))
        p.end()


class FloorMorphArea(QWidget):
    """Switches floors with a soft cross-fade + gentle scale morph instead of a sliding motion."""
    DURATION_MS = 420

    def __init__(self, pages: dict, first_key: str, parent=None):
        super().__init__(parent)
        self.pages, self.current_key = pages, first_key
        self._old = self._new = None
        self._t = 1.0
        self._animating = False
        for key, page in pages.items():
            page.setParent(self)
            page.setVisible(key == first_key)
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(self.DURATION_MS)
        self._anim.setStartValue(0.0); self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.valueChanged.connect(self._tick)
        self._anim.finished.connect(self._finish)

    def resizeEvent(self, event):
        for page in self.pages.values():
            page.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def show_floor(self, key):
        if key == self.current_key and not self._animating:
            return
        if self._animating:
            self._anim.stop(); self._finish()
            if key == self.current_key:
                return
        old, new = self.pages[self.current_key], self.pages[key]
        for page in (old, new):
            page.setGeometry(0, 0, self.width(), self.height())
            page.layout_buttons()
        new.refresh_seats()
        self._old, self._new = old.grab(), new.grab()
        old.hide(); new.hide()
        self.current_key = key
        self._animating = True
        self._t = 0.0
        self._anim.start()

    def _tick(self, value):
        self._t = float(value)
        self.update()

    def _finish(self):
        self._animating = False
        self._old = self._new = None
        self.pages[self.current_key].show()
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#ffffff"))
        if not (self._animating and self._old and self._new):
            p.end(); return
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        w, h, t = self.width(), self.height(), self._t
        c = QPointF(w / 2, h / 2)
        for pix, opacity, scale in ((self._old, 1.0 - t, 1.0 + 0.04 * t),
                                    (self._new, t, 0.96 + 0.04 * t)):
            p.save()
            p.setOpacity(opacity)
            p.translate(c); p.scale(scale, scale); p.translate(-c)
            p.drawPixmap(QRectF(0, 0, w, h), pix, QRectF(pix.rect()))
            p.restore()
        p.end()


class HeatmapPage(QWidget):
    """mode: 'student' | 'entrance' | 'librarian'"""

    def __init__(self, mode, seat_manager, student_number=None, parent=None):
        super().__init__(parent)
        self.setObjectName("pageBg")
        self.mode, self.seat_manager, self.student_number = mode, seat_manager, student_number

        body = QHBoxLayout(self); body.setContentsMargins(0, 0, 0, 0); body.setSpacing(0)
        body.addWidget(self._build_sidebar())
        self.floor_pages = {k: FloorPlanWidget(k, seat_manager, self.handle_seat_click) for k, _, _ in FLOORS}
        self.morph = FloorMorphArea(self.floor_pages, "first")
        body.addWidget(self.morph, 1)
        self.floor_buttons["first"].setChecked(True)
        self._apply_cursor_rule()

        # Real-time updates: everything repaints from the shared SeatManager once a second.
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh_all)
        self._timer.start(1000)

    # ---------- sidebar ----------
    def _build_sidebar(self):
        sidebar = QFrame(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(200)
        lay = QVBoxLayout(sidebar); lay.setContentsMargins(14, 22, 14, 18); lay.setSpacing(10)
        title = QLabel("LIBRARY"); title.setObjectName("sectionTitle")
        sub = QLabel("SELECT FLOOR"); sub.setObjectName("sectionSub")
        lay.addWidget(title); lay.addWidget(sub); lay.addSpacing(10)
        self.floor_buttons = {}
        for key, name, wing in FLOORS:
            btn = QPushButton(name if not wing else f"{name}\n({wing})")
            btn.setObjectName("floorButton"); btn.setCheckable(True); btn.setAutoExclusive(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, k=key: self.change_floor(k))
            lay.addWidget(btn); self.floor_buttons[key] = btn
        lay.addSpacing(14)

        notes = {
            "student": "Live seat status. Click a chair to reserve.",
            "entrance": "Click a chair to log a student in or out.",
            "librarian": "Click a yellow chair to see/remove its reservations, or a red chair to see/log out its occupant.",
        }
        note = QLabel(notes[self.mode]); note.setObjectName("modeNote"); note.setWordWrap(True)
        lay.addWidget(note); lay.addSpacing(10)

        lt = QLabel("Legend:"); lt.setObjectName("legendTitle"); lay.addWidget(lt)
        legend = QFrame(); legend.setObjectName("legendCard")
        g = QGridLayout(legend); g.setContentsMargins(8, 8, 8, 8); g.setHorizontalSpacing(8); g.setVerticalSpacing(6)
        for row, (status, text, color) in enumerate((("available", "Available", "#62b900"),
                                                      ("reserved", "Reserved", "#b99a00"),
                                                      ("occupied", "Occupied", "#e21b23"))):
            g.addWidget(LegendSymbol("chair", COLORS[status]), row, 0)
            lbl = QLabel(text); lbl.setStyleSheet(f"color:{color};font-size:11px;font-weight:900")
            g.addWidget(lbl, row, 1)
        g.addWidget(LegendSymbol("desk"), 3, 0)
        d = QLabel("Desk"); d.setStyleSheet("font-size:11px;font-weight:700"); g.addWidget(d, 3, 1)
        lay.addWidget(legend); lay.addStretch(1)
        return sidebar

    # ---------- behaviour ----------
    def change_floor(self, key):
        self.floor_buttons[key].setChecked(True)
        self.morph.show_floor(key)

    def _apply_cursor_rule(self):
        if self.mode == "librarian":
            for page in self.floor_pages.values():
                page.set_clickable_rule(lambda status: status in ("reserved", "occupied"))

    def refresh_all(self):
        for page in self.floor_pages.values():
            page.refresh_seats()
        self._apply_cursor_rule()

    def force_refresh(self) -> bool:
        """Used by Support → Refresh Screen."""
        for page in self.floor_pages.values():
            page.layout_buttons()
            for b in page.buttons:
                b.update_status(self.seat_manager.status(b.seat_id), force=True)
            page.update()
        self._apply_cursor_rule()
        self.morph.update(); self.update()
        return True

    def stop(self):
        self._timer.stop()

    def handle_seat_click(self, seat_id):
        if self.mode == "student":
            dlg = SeatReservationDialog(seat_id, self.seat_manager, self.student_number, self.window())
            dlg.exec()
        elif self.mode == "entrance":
            dlg = EntranceSeatDialog(seat_id, self.seat_manager, self.window())
            dlg.exec()
        else:
            status = self.seat_manager.status(seat_id)
            if status == "reserved":
                LibrarianReservationDialog(seat_id, self.seat_manager, self.refresh_all, self.window()).exec()
            elif status == "occupied":
                LibrarianOccupantDialog(seat_id, self.seat_manager, self.refresh_all, self.window()).exec()
            else:
                notify(self.window(), "Librarian access",
                       "This chair is available (green). Click a yellow or red chair to manage it.")
                return
        self.refresh_all()
