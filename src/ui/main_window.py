"""Main window for SSH key generation interface."""

import os
import sys
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFileDialog, QCheckBox, QMessageBox,
    QWidget, QGroupBox, QFormLayout, QApplication, QScrollArea
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from src.core.key_generator import KeyGenerator


def resource_path(relative_path: str) -> Path:
    """Resolve resource path for development and PyInstaller."""
    base_path = Path(getattr(sys, '_MEIPASS', Path(__file__).parent.parent.parent))
    return base_path / relative_path


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        self.setWindowTitle("SSH Key Generator")
        self.setMinimumSize(600, 750)

        icon_path = resource_path("resources/logo.ico")
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self.setWindowIcon(icon)
            if self.windowHandle():
                self.windowHandle().setIcon(icon)
            if sys.platform == 'win32':
                try:
                    from win32gui import SendMessage
                    from win32api import LoadImage
                    from win32con import IMAGE_ICON, LR_LOADFROMFILE, ICON_BIG, WM_SETICON

                    icon_handle = LoadImage(0, str(icon_path), IMAGE_ICON, 0, 0, LR_LOADFROMFILE)
                    SendMessage(self.winId().__int__(), WM_SETICON, ICON_BIG, icon_handle)
                except ImportError:
                    pass

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        scroll.setWidget(main_widget)

        title_label = QLabel("SSH Key Generator")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addSpacing(10)

        options_group = QGroupBox("Key Generation Options")
        options_group.setMinimumHeight(220)
        options_layout = QFormLayout(options_group)
        options_layout.setSpacing(12)
        options_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(options_group)

        self.key_type_combo = QComboBox()
        self.key_type_combo.addItems(["ed25519", "rsa", "ecdsa"])
        self.key_type_combo.setToolTip("Ed25519 is recommended for most use cases")
        self.key_type_combo.currentTextChanged.connect(self.update_key_bits_options)
        options_layout.addRow("Key Type:", self.key_type_combo)

        self.key_bits_combo = QComboBox()
        options_layout.addRow("Key Size:", self.key_bits_combo)
        self.update_key_bits_options(self.key_type_combo.currentText())

        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText("user@hostname (optional)")
        options_layout.addRow("Comment:", self.comment_edit)

        self.passphrase_edit = QLineEdit()
        self.passphrase_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.passphrase_edit.setPlaceholderText("Leave empty for no passphrase")
        options_layout.addRow("Passphrase:", self.passphrase_edit)

        self.confirm_passphrase_edit = QLineEdit()
        self.confirm_passphrase_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_passphrase_edit.setPlaceholderText("Confirm passphrase")
        options_layout.addRow("Confirm:", self.confirm_passphrase_edit)

        main_layout.addSpacing(15)

        output_group = QGroupBox("Output Options")
        output_group.setMinimumHeight(170)
        output_layout = QFormLayout(output_group)
        output_layout.setSpacing(12)
        output_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(output_group)

        self.default_location_check = QCheckBox("Use default location (~/.ssh)")
        self.default_location_check.setChecked(True)
        self.default_location_check.stateChanged.connect(self.toggle_output_path)
        output_layout.addRow(self.default_location_check)

        self.output_dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Output directory")
        self.output_dir_edit.setEnabled(False)
        self.output_dir_button = QPushButton("Browse...")
        self.output_dir_button.setEnabled(False)
        self.output_dir_button.clicked.connect(self.browse_output_dir)
        self.output_dir_layout.addWidget(self.output_dir_edit)
        self.output_dir_layout.addWidget(self.output_dir_button)
        output_layout.addRow("Output Directory:", self.output_dir_layout)

        self.filename_edit = QLineEdit()
        self.filename_edit.setText("id_ssh")
        self.filename_edit.setPlaceholderText("Base filename (without extension)")
        output_layout.addRow("Filename:", self.filename_edit)

        main_layout.addSpacing(30)

        self.generate_button = QPushButton("Generate SSH Key")
        self.generate_button.clicked.connect(self.generate_key)
        self.generate_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 12px;
                min-height: 50px;
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        self.generate_button.setFixedWidth(300)
        main_layout.addWidget(self.generate_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        main_layout.addSpacing(30)

        self.setup_results_area(main_layout)

        status_bar = self.statusBar()
        status_bar.setMinimumHeight(30)
        status_bar.setStyleSheet("QStatusBar { padding: 4px; }")
        status_bar.showMessage("Ready")

        self.key_generator = KeyGenerator()

    def update_key_bits_options(self, key_type):
        """Update the key bits options based on the selected key type."""
        self.key_bits_combo.clear()
        if key_type == "rsa":
            self.key_bits_combo.addItems(["2048", "3072", "4096"])
            self.key_bits_combo.setCurrentText("4096")
        elif key_type == "ed25519":
            self.key_bits_combo.addItems(["256"])
            self.key_bits_combo.setCurrentText("256")
        elif key_type == "ecdsa":
            self.key_bits_combo.addItems(["256", "384", "521"])
            self.key_bits_combo.setCurrentText("256")

    def toggle_output_path(self, state):
        """Enable or disable custom output path based on checkbox."""
        enable_custom = not state
        self.output_dir_edit.setEnabled(enable_custom)
        self.output_dir_button.setEnabled(enable_custom)

    def browse_output_dir(self):
        """Open a file dialog to select an output directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", str(Path.home()))
        if directory:
            self.output_dir_edit.setText(directory)

    def generate_key(self):
        """Generate SSH key based on selected options."""
        if self.passphrase_edit.text() != self.confirm_passphrase_edit.text():
            QMessageBox.warning(self, "Passphrase Mismatch", "The passphrases you entered do not match.")
            return

        key_type = self.key_type_combo.currentText()
        key_bits = int(self.key_bits_combo.currentText())
        comment = self.comment_edit.text().strip()
        passphrase = self.passphrase_edit.text()

        output_dir = "~/.ssh" if self.default_location_check.isChecked() else self.output_dir_edit.text()
        if not output_dir:
            QMessageBox.warning(self, "Missing Output Directory", "Please specify an output directory or use the default location.")
            return

        filename = self.filename_edit.text().strip() or "id_ssh"

        try:
            private_key_path, public_key_path = self.key_generator.generate_key(
                key_type=key_type,
                bits=key_bits,
                comment=comment,
                passphrase=passphrase,
                output_dir=output_dir,
                filename=filename
            )

            fingerprint = self.key_generator.get_fingerprint(public_key_path)

            self.private_key_label.setText(str(private_key_path))
            self.public_key_label.setText(str(public_key_path))
            self.fingerprint_label.setText(fingerprint)

            with open(public_key_path, 'r', encoding='utf-8') as f:
                self.public_key_content.setText(f.read().strip())

            self.results_group.setVisible(True)
            self.statusBar().showMessage(f"SSH key pair successfully generated: {private_key_path}")
            QMessageBox.information(self, "Success", f"SSH key pair successfully generated:\nPrivate key: {private_key_path}\nPublic key: {public_key_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate SSH key: {str(e)}")

    def open_file_location(self, path):
        """Open the file location in file explorer."""
        path = Path(path).expanduser().resolve()
        directory = path.parent

        if sys.platform == 'win32':
            os.startfile(directory)
        elif sys.platform == 'darwin':
            subprocess.run(['open', directory], check=True)
        else:
            subprocess.run(['xdg-open', directory], check=True)

    def copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        QApplication.clipboard().setText(text)
        self.statusBar().showMessage("Copied to clipboard", 2000)

    def setup_results_area(self, layout):
        """Initialize the results display group."""
        self.results_group = QGroupBox("Generated Keys")
        self.results_group.setMinimumHeight(300)
        self.results_layout = QFormLayout(self.results_group)
        self.results_layout.setSpacing(15)
        self.results_layout.setContentsMargins(20, 20, 20, 20)
        self.results_group.setVisible(False)

        field_style = """
            QLineEdit {
                padding: 8px;
                min-height: 20px;
                background-color: white;
                color: black;
                border: 1px solid #666;
                border-radius: 4px;
            }
            QLineEdit:read-only {
                background-color: #f8f8f8;
            }
        """

        button_style = """
            QPushButton {
                padding: 6px 12px;
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """

        def add_result_row(label, line_edit_attr, button_text=None, button_callback=None):
            layout_row = QHBoxLayout()
            line_edit = QLineEdit()
            line_edit.setReadOnly(True)
            line_edit.setStyleSheet(field_style)
            setattr(self, line_edit_attr, line_edit)
            layout_row.addWidget(line_edit)
            if button_text and button_callback:
                button = QPushButton(button_text)
                button.setStyleSheet(button_style)
                button.clicked.connect(button_callback)
                layout_row.addWidget(button)
            self.results_layout.addRow(label, layout_row)

        add_result_row("Private Key:", "private_key_label", "Open Location", lambda: self.open_file_location(self.private_key_label.text()))
        add_result_row("Public Key:", "public_key_label", "Open Location", lambda: self.open_file_location(self.public_key_label.text()))
        add_result_row("Fingerprint:", "fingerprint_label", "Copy", lambda: self.copy_to_clipboard(self.fingerprint_label.text()))
        add_result_row("Public Key Content:", "public_key_content", "Copy", lambda: self.copy_to_clipboard(self.public_key_content.text()))

        label_style = "QLabel { color: white; font-size: 11pt; }"
        for i in range(self.results_layout.rowCount()):
            label_item = self.results_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            if label_item and label_item.widget():
                label_item.widget().setStyleSheet(label_style)

        layout.addWidget(self.results_group)
