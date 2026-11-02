import os
import stat

import pytest

from ssh_keygen.core.key_generator import KeyGenerator


@pytest.fixture
def generator():
    return KeyGenerator()


@pytest.mark.parametrize(
    ("key_type", "bits", "prefix"),
    [
        ("ed25519", 256, "ssh-ed25519 "),
        ("rsa", 2048, "ssh-rsa "),
        ("rsa", 3072, "ssh-rsa "),
        ("rsa", 4096, "ssh-rsa "),
        ("ecdsa", 256, "ecdsa-sha2-nistp256 "),
        ("ecdsa", 384, "ecdsa-sha2-nistp384 "),
        ("ecdsa", 521, "ecdsa-sha2-nistp521 "),
    ],
)
def test_generates_each_key_type(generator, tmp_path, key_type, bits, prefix):
    private_path, public_path = generator.generate_key(
        key_type=key_type, bits=bits, output_dir=tmp_path, filename="key"
    )

    assert private_path == tmp_path / "key.pem"
    assert public_path == tmp_path / "key.pub"
    assert private_path.read_text().startswith("-----BEGIN PRIVATE KEY-----")
    assert public_path.read_text().startswith(prefix)


def test_unsupported_key_types_and_sizes_are_rejected(generator, tmp_path):
    with pytest.raises(ValueError, match="Unsupported key type"):
        generator.generate_key(key_type="dsa", output_dir=tmp_path)
    with pytest.raises(ValueError, match="Unsupported ECDSA key size"):
        generator.generate_key(key_type="ecdsa", bits=4096, output_dir=tmp_path)


def test_public_key_is_one_line_with_the_comment(generator, tmp_path):
    _, with_comment = generator.generate_key(output_dir=tmp_path, filename="a", comment="me@laptop")
    _, without_comment = generator.generate_key(output_dir=tmp_path, filename="b")

    assert with_comment.read_text().endswith(" me@laptop\n")
    assert len(without_comment.read_text().split()) == 2
    assert without_comment.read_text().endswith("\n")


def test_passphrase_encrypts_the_private_key(generator, tmp_path):
    encrypted, _ = generator.generate_key(output_dir=tmp_path, filename="a", passphrase="secret")
    plain, _ = generator.generate_key(output_dir=tmp_path, filename="b")

    assert "ENCRYPTED" in encrypted.read_text()
    assert "ENCRYPTED" not in plain.read_text()


def test_creates_the_output_directory(generator, tmp_path):
    nested = tmp_path / "keys" / "work"
    generator.generate_key(output_dir=str(nested))
    assert (nested / "id_ssh.pub").exists()


def test_refuses_to_replace_an_existing_key_unless_asked(generator, tmp_path):
    private_path, _ = generator.generate_key(output_dir=tmp_path)
    original = private_path.read_bytes()

    with pytest.raises(FileExistsError):
        generator.generate_key(output_dir=tmp_path)
    assert private_path.read_bytes() == original

    generator.generate_key(output_dir=tmp_path, overwrite=True)
    assert private_path.read_bytes() != original


@pytest.mark.skipif(os.name != "posix", reason="File modes only apply on POSIX systems")
def test_private_key_is_readable_by_its_owner_only(generator, tmp_path):
    private_path, _ = generator.generate_key(output_dir=tmp_path)
    assert stat.S_IMODE(private_path.stat().st_mode) == 0o600

    # Replacing a key resets the mode too
    private_path.chmod(0o644)
    generator.generate_key(output_dir=tmp_path, overwrite=True)
    assert stat.S_IMODE(private_path.stat().st_mode) == 0o600


def test_fingerprint(generator, tmp_path):
    public_path = tmp_path / "known.pub"
    # The fingerprint `ssh-keygen -lf` reports for this key
    public_path.write_text(
        "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDzWDkfV0noc/2zXPRSgUU/guCzc3wHJjIgujLNSqvQh me\n"
    )
    assert (
        generator.get_fingerprint(public_path)
        == "SHA256:CpFWCWzsNqeUPcgT8IabbslrO4aoS8AuoemIpFSWhJs"
    )


def test_fingerprint_of_an_invalid_file_is_rejected(generator, tmp_path):
    public_path = tmp_path / "invalid.pub"
    public_path.write_text("not-a-key")
    with pytest.raises(ValueError, match="Invalid public key format"):
        generator.get_fingerprint(public_path)
