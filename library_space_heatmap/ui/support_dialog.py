from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class SupportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Library Support")
        self.setFixedWidth(470)
        self.setStyleSheet("""
            QDialog { background:#fffdf5; }
            QLabel { font-size:14px; color:#222; }
            QLabel#title { font-size:21px; font-weight:800; color:#111; }
            QPushButton { background:#ffcc00; border:1px solid #e4b700; border-radius:8px; padding:10px 15px; font-weight:700; }
            QPushButton#secondary { background:white; border:1px solid #d7d0bd; }
        """)
        layout = QVBoxLayout(self); layout.setContentsMargins(24,24,24,22); layout.setSpacing(14)
        title = QLabel("Library View Support"); title.setObjectName("title")
        text = QLabel("This is a LIBRARY view version of the system, for further concerns like reservation, kindly access the student version or approach the librarians.")
        text.setWordWrap(True)
        layout.addWidget(title); layout.addWidget(text)
        row = QHBoxLayout(); row.addStretch()
        refresh = QPushButton("↻  Refresh Screen"); refresh.clicked.connect(self._refresh)
        close = QPushButton("Close"); close.setObjectName("secondary"); close.clicked.connect(self.accept)
        row.addWidget(refresh); row.addWidget(close); layout.addLayout(row)

    def _refresh(self):
        window = self.parent()
        if window is not None:
            for page in getattr(window, "floor_pages", {}).values():
                page.refresh_seats()
                page.repaint()
            window.update(); window.repaint()
