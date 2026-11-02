"""Application entry point."""

import ctypes
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from ssh_keygen.ui.main_window import MainWindow
from ssh_keygen.utils import resource_path

APP_ID = "SSH.KeyGenerator"


def main() -> None:
    # Without its own app ID, Windows groups the window under Python and shows Python's
    # taskbar icon
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

    app = QApplication(sys.argv)
    app.setApplicationName("SSH Key Generator")
    app.setWindowIcon(QIcon(str(resource_path("resources/logo.ico"))))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
