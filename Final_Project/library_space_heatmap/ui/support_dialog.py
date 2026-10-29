from datetime import datetime

from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ui.theme import DIALOG_STYLES


class SupportDialog(QDialog):
    """`refresh_callback` must return True if something was refreshed, False otherwise."""

    def __init__(self, context_text, refresh_callback, parent=None):
        super().__init__(parent)
        self.refresh_callback = refresh_callback
        self.setWindowTitle("Library Support")
        self.setFixedWidth(470)
        self.setStyleSheet(DIALOG_STYLES)
        lay = QVBoxLayout(self); lay.setContentsMargins(24, 24, 24, 22); lay.setSpacing(14)
        title = QLabel("Library Support"); title.setObjectName("title")
        text = QLabel(context_text); text.setWordWrap(True)
        self.feedback = QLabel(""); self.feedback.setObjectName("ok"); self.feedback.setWordWrap(True)
        lay.addWidget(title); lay.addWidget(text); lay.addWidget(self.feedback)
        row = QHBoxLayout(); row.addStretch()
        refresh = QPushButton("↻  Refresh Screen"); refresh.clicked.connect(self._refresh)
        close = QPushButton("Close"); close.setObjectName("secondary"); close.clicked.connect(self.accept)
        row.addWidget(refresh); row.addWidget(close); lay.addLayout(row)

    def _refresh(self):
        stamp = datetime.now().strftime("%I:%M:%S %p")
        if self.refresh_callback():
            self.feedback.setText(f"✓ Screen refreshed at {stamp}.")
        else:
            self.feedback.setText("There is nothing to refresh on this screen.")
