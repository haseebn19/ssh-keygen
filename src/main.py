"""SSH Key Generator application entry point."""

import sys
import ctypes
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.ui.main_window import MainWindow

APP_ID = 'SSH.KeyGenerator.1.0'


def set_taskbar_icon() -> None:
    """Set application ID for Windows taskbar grouping."""
    if sys.platform == 'win32':
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except Exception as e:
            if __debug__:
                print(f"Failed to set taskbar icon: {e}")


def resource_path(relative_path: str) -> Path:
    """Resolve resource path for development and PyInstaller."""
    base_path = Path(getattr(sys, '_MEIPASS', Path(__file__).parent.parent))
    return base_path / relative_path


def main() -> None:
    """Initialize and run the application."""
    set_taskbar_icon()

    app = QApplication(sys.argv)
    app.setApplicationName("SSH Key Generator")

    icon_path = resource_path("resources/logo.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
