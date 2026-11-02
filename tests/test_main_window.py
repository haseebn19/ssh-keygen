import os
import sys
from unittest.mock import patch

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QMessageBox

from ssh_keygen.ui.main_window import MainWindow


def combo_items(combo) -> list[str]:
    return [combo.itemText(i) for i in range(combo.count())]


@pytest.fixture(scope="module", autouse=True)
def qapp():
    yield QApplication.instance() or QApplication(sys.argv)


@pytest.fixture
def window(tmp_path):
    win = MainWindow()
    win.default_location_check.setChecked(False)
    win.output_dir_edit.setText(str(tmp_path))
    yield win
    win.close()


def test_key_sizes_follow_the_key_type(window):
    assert combo_items(window.key_bits_combo) == ["256"]
    window.key_type_combo.setCurrentText("rsa")
    assert combo_items(window.key_bits_combo) == ["2048", "3072", "4096"]
    assert window.key_bits_combo.currentText() == "4096"


def test_generating_a_key_shows_the_results(window, tmp_path):
    window.comment_edit.setText("me@laptop")
    window.generate_key()

    assert window.results_group.isVisibleTo(window)
    assert window.private_key_path_field.text() == str(tmp_path / "id_ssh.pem")
    assert window.fingerprint_field.text().startswith("SHA256:")
    assert window.public_key_field.text().endswith(" me@laptop")
    assert window.statusBar().currentMessage() == "Generated id_ssh.pem and id_ssh.pub"


def test_mismatched_passphrases_are_not_used(window, tmp_path):
    window.passphrase_edit.setText("one")
    window.confirm_passphrase_edit.setText("two")
    with patch.object(QMessageBox, "warning") as warning:
        window.generate_key()

    warning.assert_called_once()
    assert not (tmp_path / "id_ssh.pem").exists()


def test_replacing_a_key_needs_confirmation(window, tmp_path):
    window.generate_key()
    original = (tmp_path / "id_ssh.pem").read_bytes()

    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No):
        window.generate_key()
    assert (tmp_path / "id_ssh.pem").read_bytes() == original

    with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
        window.generate_key()
    assert (tmp_path / "id_ssh.pem").read_bytes() != original
