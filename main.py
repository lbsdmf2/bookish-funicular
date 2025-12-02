# main.py
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.config_manager import ConfigManager

if __name__ == "__main__":
    ConfigManager.ensure_default()
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
