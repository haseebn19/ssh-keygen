"""Application entry point."""

import contextlib
import ctypes
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from ssh_keygen.ui.main_window import MainWindow
from ssh_keygen.utils import resource_path

APP_ID = "SSH.KeyGenerator.1.0"


def set_taskbar_icon() -> None:
    """Set Windows taskbar app ID."""
    if sys.platform == "win32":
        with contextlib.suppress(Exception):
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(ctypes.c_wchar_p(APP_ID))


def main() -> None:
    """Run the application."""
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
