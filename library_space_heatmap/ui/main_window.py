import json
import os
from PyQt6.QtCore import Qt, QRect, QRectF, QSize, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QFont, QPainterPath
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QMessageBox, QDialog, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QFrame, QGridLayout, QStackedWidget,
    QSizePolicy, QGraphicsDropShadowEffect
)
from core.seat_manager import SeatManager
from ui.login_dialog import SeatLoginDialog
from ui.support_dialog import SupportDialog

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

FLOORS = [
    ("first", "First Floor", "01"),
    ("right", "Second Floor", "RIGHT WING"),
    ("left", "Second Floor", "LEFT WING"),
]

# Logical drawing area traced from the supplied reference screenshots.
# All architecture is drawn with QPainter (no screenshot is used as a background).
FLOOR_FILES = {
    "first": ("", QRect(152, 88, 886, 497)),
    "right": ("", QRect(151, 88, 885, 496)),
    "left": ("", QRect(151, 88, 889, 496)),
}

STYLES = """
QMainWindow, QWidget#appRoot { background: #fffdf5; color: #191919; }
QFrame#topHeader { background: #ffcc00; border-bottom: 4px solid #111111; }
QLabel#brandTitle { font-size: 22px; font-weight: 900; color: #111111; }
QLabel#brandSubtitle { font-size: 13px; color: #28220a; }
QFrame#sidebar { background: #fffdf5; border-right: 1px solid #e5dcc2; }
QLabel#sectionTitle { font-size: 20px; font-weight: 900; color: #171717; }
QLabel#sectionSub { font-size: 10px; color: #8a7100; font-weight: 800; letter-spacing: 1px; }
QPushButton#floorButton { text-align: left; background: #ffffff; color: #242424;
 border: 1px solid #e7dfcb; border-left: 4px solid #e7dfcb; border-radius: 9px;
 padding: 12px 10px; font-size: 12px; font-weight: 600; min-height: 48px; }
QPushButton#floorButton:hover { background: #fff4bd; border-color: #e8c000; }
QPushButton#floorButton:checked { background: #ffcc00; border: 1px solid #e5b900;
 border-left: 5px solid #111111; color: #111111; font-weight: 900; }
QPushButton#supportButton { background: #ffdc45; border: 1px solid #e3b900; border-radius: 9px;
 padding: 10px 15px; font-weight: 800; color: #111111; }
QPushButton#supportButton:hover { background: #ffe77c; }
QFrame#footer { background: #ffcc00; border-top: 4px solid #111111; }
QLabel#footerText { font-size: 11px; font-weight: 800; color: #171717; }
QLabel#legendTitle { font-weight: 800; font-size: 12px; }
QLabel#legendText { font-size: 11px; color: #393939; }
QFrame#legendCard { background: #fff6d5; border: 1px solid #f0e4b8; border-radius: 8px; }
"""

class SeatButton(QPushButton):
    """A genuine clickable Qt button painted to match the supplied chair icons."""
    def __init__(self, seat_id, side_view, callback, parent=None):
        super().__init__(parent)
        self.seat_id = seat_id
        self.side_view = side_view
        self.occupied = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setToolTip(f"Seat {seat_id} — Available")
        self.clicked.connect(lambda: callback(self.seat_id))
        self.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0; } QPushButton:hover { background: rgba(255,204,0,35); }")
        self.setAccessibleName(f"Library seat {seat_id}")

    def set_occupied(self, occupied):
        self.occupied = occupied
        self.setToolTip(f"Seat {self.seat_id} — {'Occupied' if occupied else 'Available'}")
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        r = QRectF(self.rect()).adjusted(1.2, 1.2, -1.2, -1.2)
        fill = QColor("#ff575d" if self.occupied else "#b8ff72")
        pen = QPen(QColor("#101010"))
        pen.setWidthF(max(1.1, min(2.0, min(r.width(), r.height()) * .075)))
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(fill)
        if self.side_view and r.width() > r.height() * .70:
            # Side-view chair: curved backrest, padded seat and two supports.
            path = QPainterPath()
            path.moveTo(r.left()+r.width()*.22, r.top()+r.height()*.12)
            path.cubicTo(r.left()+r.width()*.06, r.top()+r.height()*.08,
                         r.left()+r.width()*.06, r.bottom()-r.height()*.08,
                         r.left()+r.width()*.22, r.bottom()-r.height()*.10)
            path.cubicTo(r.left()+r.width()*.30, r.bottom()-r.height()*.14,
                         r.left()+r.width()*.29, r.top()+r.height()*.14,
                         r.left()+r.width()*.22, r.top()+r.height()*.12)
            p.drawPath(path)
            p.drawRoundedRect(QRectF(r.left()+r.width()*.25, r.top()+r.height()*.22,
                                     r.width()*.68, r.height()*.56), r.width()*.09, r.height()*.09)
            sw, sh = r.width()*.40, max(2, r.height()*.12)
            sx = r.left()+r.width()*.49
            p.drawRoundedRect(QRectF(sx, r.top()+r.height()*.04, sw, sh), 2, 2)
            p.drawRoundedRect(QRectF(sx, r.bottom()-sh-r.height()*.04, sw, sh), 2, 2)
        else:
            band_h = max(2.4, r.height()*.20)
            body = QRectF(r.left(), r.top(), r.width(), r.height()-band_h*.52)
            radius = min(r.width()*.23, r.height()*.28)
            p.drawRoundedRect(body, radius, radius)
            p.drawRect(QRectF(r.left(), r.bottom()-band_h, r.width(), band_h))
        if self.underMouse():
            p.setBrush(Qt.BrushStyle.NoBrush)
            hover_pen = QPen(QColor("#e5ae00")); hover_pen.setWidthF(1.2)
            p.setPen(hover_pen); p.drawRoundedRect(r.adjusted(-.5,-.5,.5,.5), 3, 3)
        p.end()

class LegendSymbol(QWidget):
    """Small vector-drawn chair/desk symbol used by the reference-style legend."""
    def __init__(self, kind="chair", color="#b8ff72", parent=None):
        super().__init__(parent)
        self.kind = kind
        self.color = QColor(color)
        self.setFixedSize(28 if kind == "chair" else 54, 24)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen = QPen(QColor("#111111"), 1.25)
        p.setPen(pen)
        if self.kind == "desk":
            p.setBrush(QColor("#ffffff"))
            p.drawRect(QRectF(1.5, 3, self.width()-3, self.height()-6))
        elif self.kind == "side":
            p.setBrush(self.color)
            p.drawRoundedRect(QRectF(1, 4, 6, 16), 2, 2)
            p.drawRoundedRect(QRectF(7, 7, 17, 10), 2, 2)
            p.drawRoundedRect(QRectF(10, 1.5, 11, 4), 1.5, 1.5)
            p.drawRoundedRect(QRectF(10, 18, 11, 4), 1.5, 1.5)
        else:
            p.setBrush(self.color)
            p.drawRoundedRect(QRectF(3, 2, 21, 18), 4, 4)
            p.drawRect(QRectF(3, 15, 21, 4))
        p.end()


class FloorPlanWidget(QWidget):
    def __init__(self, floor_key, seat_manager, seat_callback, parent=None):
        super().__init__(parent)
        self.floor_key = floor_key
        self.seat_manager = seat_manager
        self.seat_callback = seat_callback
        self.setMinimumSize(540, 360)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        with open(os.path.join(ROOT, "chair_positions.json"), encoding="utf-8") as f:
            self.positions = json.load(f)[floor_key]
        # Floor plans are drawn entirely with QPainter. Reference screenshots are
        # guides only and are deliberately NOT loaded as the plan background.
        _, logical_rect = FLOOR_FILES[floor_key]
        self.source_crop = logical_rect
        self.plan_width = logical_rect.width()
        self.plan_height = logical_rect.height()
        self.buttons = []
        for i, box in enumerate(self.positions, start=1):
            seat_id = f"{floor_key}-{i:03d}"
            # Larger, portrait-oriented positions are the side chairs from the reference.
            side_view = box[2] >= 25 and box[3] >= 25
            button = SeatButton(seat_id, side_view, self.seat_callback, self)
            button.set_occupied(self.seat_manager.status(seat_id) == "occupied")
            button._source_box = box
            self.buttons.append(button)
        self._layout_buttons()

    def resizeEvent(self, event):
        self._layout_buttons()
        super().resizeEvent(event)

    def _layout_buttons(self):
        if not self.buttons:
            return
        sx = self.width() / self.plan_width
        sy = self.height() / self.plan_height
        for button in self.buttons:
            x, y, w, h = button._source_box
            x -= self.source_crop.x(); y -= self.source_crop.y()
            # Keep each hitbox tightly around its own drawn chair.
            button.setGeometry(round(x*sx), round(y*sy),
                               max(9, round(w*sx)), max(9, round(h*sy)))

    def refresh_seats(self):
        for button in self.buttons:
            button.set_occupied(self.seat_manager.status(button.seat_id) == "occupied")
        self.update()

    def _draw_desk(self, p, x, y, w, h):
        p.setPen(QPen(QColor("#222222"), 1.8))
        p.setBrush(QColor("#ffffff"))
        p.drawRect(QRectF(x, y, w, h))

    def _draw_shelf(self, p, x, y, w, h, vertical=True):
        p.setPen(QPen(QColor("#777777"), 1.0))
        p.setBrush(QColor("#fbfbfb"))
        p.drawRect(QRectF(x, y, w, h))
        p.setPen(QPen(QColor("#9b9b9b"), 1.0))
        if vertical:
            p.drawRect(QRectF(x+w*.42, y+5, w*.16, max(5, h-10)))
        else:
            p.drawRect(QRectF(x+5, y+h*.42, max(5, w-10), h*.16))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.fillRect(self.rect(), QColor("#ffffff"))
        p.save()
        p.scale(self.width()/self.plan_width, self.height()/self.plan_height)

        black = QColor("#202020")
        white = QColor("#ffffff")
        green = QColor("#b8ff72")
        shelf_fill = QColor("#fdfdfd")
        p.setPen(QPen(black, 1.8))
        p.setBrush(white)

        def desk(x, y, w, h, line=1.8):
            p.setPen(QPen(black, line)); p.setBrush(white)
            p.drawRect(QRectF(x, y, w, h))

        def shelf(x, y, w, h, vertical=True):
            p.setPen(QPen(QColor("#777777"), 1.0)); p.setBrush(shelf_fill)
            p.drawRect(QRectF(x, y, w, h))
            p.setPen(QPen(QColor("#a0a0a0"), 1.0))
            if vertical:
                p.drawRect(QRectF(x+w*.43, y+5, max(2,w*.14), max(3,h-10)))
            else:
                p.drawRect(QRectF(x+5, y+h*.43, max(3,w-10), max(2,h*.14)))

        def side_panels(x, y, w, heights):
            yy = y
            p.setPen(QPen(black, 1.8)); p.setBrush(green)
            for h in heights:
                p.drawRect(QRectF(x, yy, w, h)); yy += h

        if self.floor_key == "first":
            # Entrance and upper counters, traced to the first-floor reference.
            p.setPen(QPen(black, 2.2)); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawLine(151, 0, 205, 0)
            p.drawLine(151, 0, 151, 11)
            p.drawArc(QRectF(151, 0, 58, 58), -90*16, 90*16)
            p.save(); p.translate(131, 11); p.rotate(90)
            p.setPen(QPen(black, 1)); p.drawText(QRectF(0,0,60,18), Qt.AlignmentFlag.AlignCenter, "Entrance"); p.restore()
            desk(257, 0, 114, 36); desk(371, 0, 115, 36); desk(696, 0, 116, 36)
            # Five green study counter panels and the narrow shelf beside each.
            side_panels(114, 77, 36, [83,84,84,84,83])
            for y,h in [(77,82),(159,84),(243,84),(327,84),(411,85)]: shelf(153,y,31,h)
            # Four paired study-desk rows, each desk exactly separated from its chairs.
            for x in (270,588):
                for y in (115,217,319,421): desk(x,y,115,36)
            # Central shelf trio and right-hand tall shelf, with visible section breaks.
            for y,h in [(93,84),(209,84),(325,84)]: shelf(472,y,31,h)
            for y,h in [(69,84),(153,84),(237,84),(321,84),(405,92)]: shelf(777,y,31,h)

        elif self.floor_key == "right":
            # Right-wing entrance, service counter, and side work area.
            p.setPen(QPen(black, 2.2)); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawLine(82, 0, 82, 118)
            p.drawArc(QRectF(82, 0, 56, 58), 180*16, 90*16)
            p.drawLine(82, 0, 137, 0)
            p.drawText(QRectF(45, 25, 30, 70), Qt.AlignmentFlag.AlignCenter, "Entrance")
            desk(218,0,116,33); desk(334,0,116,33)
            # Service zone at left: top counter, divider, and lower counter.
            desk(82,119,117,36); desk(82,295,117,37)
            p.setPen(QPen(black,1.8)); p.setBrush(white)
            p.drawRect(QRectF(82,155,79,140)); p.drawRect(QRectF(161,155,38,117))
            # The upper-right desk is offset; lower rows form two distinct banks.
            desk(576,7,115,36)
            for x in (318,576):
                for y in (116,215,314,413): desk(x,y,115,36)
            for y,h in [(0,80),(85,80),(170,80),(255,80),(340,80),(420,77)]: shelf(778,y,31,h)

        else:
            # Second-floor left wing: centered double entrance and upper counters.
            p.setPen(QPen(black, 2.2)); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawLine(76, 0, 76, 34); p.drawLine(192, 0, 192, 34)
            p.drawArc(QRectF(76, 0, 58, 58), 180*16, 90*16)
            p.drawArc(QRectF(134, 0, 58, 58), -90*16, 90*16)
            p.drawText(QRectF(83, 0, 103, 20), Qt.AlignmentFlag.AlignCenter, "Entrance")
            desk(223,0,116,34); desk(339,0,116,34)
            # Four green counter panels on the left with shelves alongside.
            side_panels(115,160,36,[84,84,84,85])
            for y,h in [(160,83),(243,84),(327,84),(411,85)]: shelf(153,y,31,h)
            for x in (270,588):
                for y in (115,217,319,421): desk(x,y,115,36)
            for y,h in [(93,84),(209,84),(325,84)]: shelf(472,y,31,h)
            for y,h in [(0,84),(84,84),(168,84),(252,84),(336,84),(420,77)]: shelf(780,y,30,h)

        # Fine floor boundary only; desks and shelves remain white with black outlines.
        p.setPen(QPen(QColor("#eeeeee"), 1)); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(QRectF(.5,.5,self.plan_width-1,self.plan_height-1))
        p.restore(); p.end()

class FloorSlideArea(QWidget):
    """Hosts each floor and slides the new plan in when a floor button is pressed."""
    def __init__(self, floors, parent=None):
        super().__init__(parent)
        self.pages = floors
        self.current_key = "first"
        self._animations = []
        for page in self.pages.values():
            page.setParent(self)
        self.pages[self.current_key].show()

    def resizeEvent(self, event):
        current = self.pages[self.current_key]
        current.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def show_floor(self, key):
        if key == self.current_key:
            return
        old_key = self.current_key
        old_page, new_page = self.pages[old_key], self.pages[key]
        direction = 1 if [x[0] for x in FLOORS].index(key) > [x[0] for x in FLOORS].index(old_key) else -1
        w, h = self.width(), self.height()
        new_page.setGeometry(direction*w, 0, w, h)
        new_page.show(); new_page.raise_()
        old_anim = QPropertyAnimation(old_page, b"pos", self)
        old_anim.setDuration(300); old_anim.setStartValue(QPoint(0, 0)); old_anim.setEndValue(QPoint(-direction*w, 0))
        old_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        new_anim = QPropertyAnimation(new_page, b"pos", self)
        new_anim.setDuration(300); new_anim.setStartValue(QPoint(direction*w, 0)); new_anim.setEndValue(QPoint(0, 0))
        new_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animations = [old_anim, new_anim]
        old_anim.start(); new_anim.start()
        self.current_key = key
        def finish():
            old_page.hide(); old_page.move(0, 0)
            new_page.setGeometry(0, 0, self.width(), self.height())
            self._animations = []
        new_anim.finished.connect(finish)

class LibraryHeatMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TIP Integrated Library Services | Library Space Heat Map")
        self.resize(1240, 760)
        self.setMinimumSize(1000, 650)
        self.seat_manager = SeatManager()
        self.setStyleSheet(STYLES)
        root = QWidget(); root.setObjectName("appRoot")
        outer = QVBoxLayout(root); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
        outer.addWidget(self._build_header())
        body = QHBoxLayout(); body.setContentsMargins(0,0,0,0); body.setSpacing(0)
        body.addWidget(self._build_sidebar())
        self.floor_pages = {key: FloorPlanWidget(key, self.seat_manager, self.handle_seat_click) for key, _, _ in FLOORS}
        self.slide_area = FloorSlideArea(self.floor_pages)
        body.addWidget(self.slide_area, 1)
        body_wrap = QWidget(); body_wrap.setLayout(body); outer.addWidget(body_wrap, 1)
        outer.addWidget(self._build_footer())
        self.setCentralWidget(root)
        self.floor_buttons["first"].setChecked(True)

    def _build_header(self):
        header = QFrame(); header.setObjectName("topHeader"); header.setFixedHeight(92)
        layout = QHBoxLayout(header); layout.setContentsMargins(24,10,24,10); layout.setSpacing(16)
        logo = QLabel(); logo.setFixedSize(76,60); logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = QPixmap(os.path.join(ASSETS, "tip_logo.png"))
        if not pix.isNull(): logo.setPixmap(pix.scaled(76,60,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        logo.setStyleSheet("background:white;border:1px solid #111")
        layout.addWidget(logo)
        brand = QVBoxLayout(); brand.setSpacing(2)
        title = QLabel("TECHNOLOGICAL INSTITUTE OF THE PHILIPPINES"); title.setObjectName("brandTitle")
        subtitle = QLabel("Integrated Library Services"); subtitle.setObjectName("brandSubtitle")
        brand.addWidget(title); brand.addWidget(subtitle); layout.addLayout(brand,1)
        support = QPushButton("◉  Support"); support.setObjectName("supportButton"); support.setCursor(Qt.CursorShape.PointingHandCursor)
        support.clicked.connect(self.open_support); layout.addWidget(support)
        return header

    def _build_sidebar(self):
        sidebar = QFrame(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(190)
        layout = QVBoxLayout(sidebar); layout.setContentsMargins(14,22,14,18); layout.setSpacing(10)
        title = QLabel("LIBRARY"); title.setObjectName("sectionTitle"); layout.addWidget(title)
        sub = QLabel("SELECT FLOOR"); sub.setObjectName("sectionSub"); layout.addWidget(sub); layout.addSpacing(12)
        self.floor_buttons = {}
        for key, name, wing in FLOORS:
            btn = QPushButton()
            btn.setObjectName("floorButton"); btn.setCheckable(True); btn.setAutoExclusive(True)
            btn.setText(name if key == "first" else f"{name}\n({wing.title()})")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, k=key: self.change_floor(k))
            layout.addWidget(btn); self.floor_buttons[key] = btn
        layout.addSpacing(24)
        legend_title = QLabel("Legend:"); legend_title.setObjectName("legendTitle"); layout.addWidget(legend_title)
        legend = QFrame(); legend.setObjectName("legendCard")
        leg = QGridLayout(legend); leg.setContentsMargins(6,6,6,6); leg.setHorizontalSpacing(4); leg.setVerticalSpacing(3)
        chairs_label = QLabel("Chairs"); chairs_label.setAlignment(Qt.AlignmentFlag.AlignCenter); chairs_label.setStyleSheet("font-size:10px;font-weight:700")
        desk_label = QLabel("Desk"); desk_label.setAlignment(Qt.AlignmentFlag.AlignCenter); desk_label.setStyleSheet("font-size:10px;font-weight:700")
        leg.addWidget(chairs_label,0,0,1,2); leg.addWidget(desk_label,0,2)
        leg.addWidget(LegendSymbol("chair", "#b8ff72"),1,0,Qt.AlignmentFlag.AlignCenter)
        leg.addWidget(LegendSymbol("side", "#b8ff72"),1,1,Qt.AlignmentFlag.AlignCenter)
        leg.addWidget(LegendSymbol("desk"),1,2,Qt.AlignmentFlag.AlignCenter)
        # The reference legend labels the three states with colored text, not swatches.
        occupied = QLabel("Occupied"); occupied.setStyleSheet("color:#e21b23;font-size:10px;font-weight:900")
        reserved = QLabel("Reserved"); reserved.setStyleSheet("color:#b99a00;font-size:10px;font-weight:900")
        available = QLabel("Available"); available.setStyleSheet("color:#62b900;font-size:10px;font-weight:900")
        leg.addWidget(occupied,2,0,1,2,Qt.AlignmentFlag.AlignCenter)
        leg.addWidget(reserved,2,2,Qt.AlignmentFlag.AlignCenter)
        leg.addWidget(available,3,0,1,3,Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(legend); layout.addStretch(1)
        tip = QLabel("TIP\nINTEGRATED LIBRARY SERVICES"); tip.setStyleSheet("font-size:9px;color:#7b6d43")
        layout.addWidget(tip)
        return sidebar

    def _build_footer(self):
        footer = QFrame(); footer.setObjectName("footer"); footer.setFixedHeight(42)
        layout = QHBoxLayout(footer); layout.setContentsMargins(10,0,10,0)
        text = QLabel("© 2026 Technological Institute of the Philippines. All Rights Reserved.")
        text.setObjectName("footerText"); text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text); return footer

    def change_floor(self, key):
        self.floor_buttons[key].setChecked(True)
        self.slide_area.show_floor(key)

    def open_support(self):
        dialog = SupportDialog(self)
        dialog.exec()

    def handle_seat_click(self, seat_id):
        current = self.seat_manager.status(seat_id)
        dialog = SeatLoginDialog(seat_id, current, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        student_number = dialog.student_number().strip()
        if not student_number:
            QMessageBox.warning(self, "Student number required", "Please enter your student number.")
            return
        if current == "available":
            ok, message = self.seat_manager.occupy(seat_id, student_number)
        else:
            ok, message = self.seat_manager.release(seat_id, student_number)
        if ok:
            for page in self.floor_pages.values(): page.refresh_seats()
        else:
            QMessageBox.warning(self, "Seat access", message)
