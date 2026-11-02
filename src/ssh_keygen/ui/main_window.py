"""Main window UI."""

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ssh_keygen.core.key_generator import KeyGenerator
from ssh_keygen.utils import sanitize_filename


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("SSH Key Generator")
        self.setMinimumSize(600, 750)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(self.scroll_area)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.scroll_area.setWidget(main_widget)

        title_label = QLabel("SSH Key Generator")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addSpacing(10)

        options_group = QGroupBox("Key Generation Options")
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
        output_layout = QFormLayout(output_group)
        output_layout.setSpacing(12)
        output_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(output_group)

        self.default_location_check = QCheckBox("Use default location (~/.ssh)")
        self.default_location_check.setChecked(True)
        self.default_location_check.toggled.connect(self.toggle_output_path)
        output_layout.addRow(self.default_location_check)

        output_dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Output directory")
        self.output_dir_edit.setEnabled(False)
        self.output_dir_button = QPushButton("Browse...")
        self.output_dir_button.setEnabled(False)
        self.output_dir_button.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(self.output_dir_edit)
        output_dir_layout.addWidget(self.output_dir_button)
        output_layout.addRow("Output Directory:", output_dir_layout)

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

    def update_key_bits_options(self, key_type: str) -> None:
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

    def toggle_output_path(self, use_default: bool) -> None:
        self.output_dir_edit.setEnabled(not use_default)
        self.output_dir_button.setEnabled(not use_default)

    def browse_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", str(Path.home())
        )
        if directory:
            self.output_dir_edit.setText(directory)

    def generate_key(self) -> None:
        if self.passphrase_edit.text() != self.confirm_passphrase_edit.text():
            QMessageBox.warning(
                self, "Passphrase Mismatch", "The passphrases you entered do not match."
            )
            return

        key_type = self.key_type_combo.currentText()
        key_bits = int(self.key_bits_combo.currentText())
        comment = self.comment_edit.text().strip()
        passphrase = self.passphrase_edit.text()

        output_dir = (
            "~/.ssh" if self.default_location_check.isChecked() else self.output_dir_edit.text()
        )
        if not output_dir:
            QMessageBox.warning(
                self,
                "Missing Output Directory",
                "Please specify an output directory or use the default location.",
            )
            return

        filename = sanitize_filename(self.filename_edit.text())

        existing = [
            path for path in self.key_generator.key_paths(output_dir, filename) if path.exists()
        ]
        if existing and not self.confirm_replace(existing[0]):
            return

        try:
            private_key_path, public_key_path = self.key_generator.generate_key(
                key_type=key_type,
                bits=key_bits,
                comment=comment,
                passphrase=passphrase,
                output_dir=output_dir,
                filename=filename,
                overwrite=bool(existing),
            )

            self.private_key_path_field.setText(str(private_key_path))
            self.public_key_path_field.setText(str(public_key_path))
            self.fingerprint_field.setText(self.key_generator.get_fingerprint(public_key_path))
            self.public_key_field.setText(public_key_path.read_text(encoding="utf-8").strip())

            self.results_group.setVisible(True)
            self.statusBar().showMessage(
                f"Generated {private_key_path.name} and {public_key_path.name}"
            )
            # Wait for the layout to make room for the results before scrolling to them
            QTimer.singleShot(0, lambda: self.scroll_area.ensureWidgetVisible(self.results_group))

        except (OSError, ValueError) as e:
            QMessageBox.critical(self, "Error", f"Could not generate the key: {e}")

    def confirm_replace(self, existing_path: Path) -> bool:
        """Ask before overwriting a key, since the old private key cannot be recovered."""
        answer = QMessageBox.question(
            self,
            "Replace Existing Key?",
            f"{existing_path.name} already exists in {existing_path.parent}.\n\n"
            "Replacing it permanently deletes the current key. Any server that uses it "
            "will stop accepting it. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def open_file_location(self, path: str) -> None:
        directory = Path(path).expanduser().resolve().parent
        try:
            if sys.platform == "win32":
                os.startfile(directory)
            elif sys.platform == "darwin":
                subprocess.run(["open", directory], check=True)
            else:
                subprocess.run(["xdg-open", directory], check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            QMessageBox.warning(self, "Could Not Open Folder", f"Could not open {directory}: {e}")

    def copy_to_clipboard(self, text: str) -> None:
        QApplication.clipboard().setText(text)
        self.statusBar().showMessage("Copied to clipboard", 2000)

    def setup_results_area(self, layout: QVBoxLayout) -> None:
        self.results_group = QGroupBox("Generated Keys")
        results_layout = QFormLayout(self.results_group)
        results_layout.setSpacing(15)
        results_layout.setContentsMargins(20, 20, 20, 20)
        self.results_group.setVisible(False)

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

        def add_result_row(
            label: str, button_text: str, action: Callable[[str], None]
        ) -> QLineEdit:
            """Add a read-only field with a button that calls `action` with the field's text."""
            field = QLineEdit()
            field.setReadOnly(True)
            button = QPushButton(button_text)
            button.setStyleSheet(button_style)
            button.clicked.connect(lambda: action(field.text()))
            row = QHBoxLayout()
            row.addWidget(field)
            row.addWidget(button)
            results_layout.addRow(label, row)
            return field

        self.private_key_path_field = add_result_row(
            "Private Key:", "Open Location", self.open_file_location
        )
        self.public_key_path_field = add_result_row(
            "Public Key:", "Open Location", self.open_file_location
        )
        self.fingerprint_field = add_result_row("Fingerprint:", "Copy", self.copy_to_clipboard)
        self.public_key_field = add_result_row(
            "Public Key Content:", "Copy", self.copy_to_clipboard
        )

        layout.addWidget(self.results_group)
