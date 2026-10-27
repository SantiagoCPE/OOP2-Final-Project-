from PyQt6.QtWidgets import QApplication
from ui.main_window import LibraryHeatMapWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("TIP Library Space Heat Map")
    window = LibraryHeatMapWindow()
    window.show()
    sys.exit(app.exec())
