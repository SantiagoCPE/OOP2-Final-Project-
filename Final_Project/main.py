import os
import sys

# Make the library_space_heatmap folder importable (core/, ui/)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "library_space_heatmap"))

from PyQt6.QtWidgets import QApplication
from ui.app_window import AppWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("TIP Library Space Heat Map")
    window = AppWindow()
    window.show()
    sys.exit(app.exec())
