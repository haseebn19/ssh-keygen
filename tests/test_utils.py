import sys

import pytest

from ssh_keygen.utils import resource_path, sanitize_filename


def test_resource_path_finds_packaged_files():
    assert resource_path("resources/logo.ico").is_file()


def test_resource_path_uses_the_pyinstaller_folder(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert resource_path("resources/logo.ico") == tmp_path / "resources" / "logo.ico"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("id_rsa", "id_rsa"),
        ("file.name.txt", "file.name.txt"),
        ('a<b>c:d"e/f\\g|h?i*j', "a_b_c_d_e_f_g_h_i_j"),
        ("  \tkey\n", "key"),
        ("...key...", "key"),
    ],
)
def test_sanitize_filename(name, expected):
    assert sanitize_filename(name) == expected


@pytest.mark.parametrize("name", ["", "   ", "...", "<<<>>>"])
def test_sanitize_filename_falls_back_to_the_default(name):
    assert sanitize_filename(name) == "id_ssh"
