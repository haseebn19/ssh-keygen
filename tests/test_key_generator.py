"""Tests for SSH key generator functionality."""

import shutil
import tempfile
from pathlib import Path

import pytest

from src.core.key_generator import KeyGenerator


class TestKeyGenerator:
    """Tests for KeyGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create a KeyGenerator instance."""
        return KeyGenerator()

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for key output."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)

    # ----- ED25519 Tests -----

    def test_generate_ed25519_key(self, generator, temp_dir):
        """Should generate ED25519 key pair."""
        private_path, public_path = generator.generate_key(
            key_type="ed25519", output_dir=temp_dir, filename="test_ed25519"
        )

        assert private_path.exists()
        assert public_path.exists()
        assert private_path.suffix == ".pem"
        assert public_path.suffix == ".pub"

    def test_ed25519_public_key_format(self, generator, temp_dir):
        """ED25519 public key should have correct format."""
        _, public_path = generator.generate_key(
            key_type="ed25519", output_dir=temp_dir, filename="test_ed25519"
        )

        content = public_path.read_text()
        assert content.startswith("ssh-ed25519 ")

    # ----- RSA Tests -----

    def test_generate_rsa_key(self, generator, temp_dir):
        """Should generate RSA key pair."""
        private_path, public_path = generator.generate_key(
            key_type="rsa",
            bits=2048,  # Use smaller key for faster tests
            output_dir=temp_dir,
            filename="test_rsa",
        )

        assert private_path.exists()
        assert public_path.exists()

    def test_rsa_public_key_format(self, generator, temp_dir):
        """RSA public key should have correct format."""
        _, public_path = generator.generate_key(
            key_type="rsa", bits=2048, output_dir=temp_dir, filename="test_rsa"
        )

        content = public_path.read_text()
        assert content.startswith("ssh-rsa ")

    @pytest.mark.parametrize("bits", [2048, 3072, 4096])
    def test_rsa_key_sizes(self, generator, temp_dir, bits):
        """Should generate RSA keys with different sizes."""
        private_path, public_path = generator.generate_key(
            key_type="rsa", bits=bits, output_dir=temp_dir, filename=f"test_rsa_{bits}"
        )

        assert private_path.exists()
        assert public_path.exists()

    # ----- ECDSA Tests -----

    def test_generate_ecdsa_key(self, generator, temp_dir):
        """Should generate ECDSA key pair."""
        private_path, public_path = generator.generate_key(
            key_type="ecdsa", bits=256, output_dir=temp_dir, filename="test_ecdsa"
        )

        assert private_path.exists()
        assert public_path.exists()

    def test_ecdsa_public_key_format(self, generator, temp_dir):
        """ECDSA public key should have correct format."""
        _, public_path = generator.generate_key(
            key_type="ecdsa", bits=256, output_dir=temp_dir, filename="test_ecdsa"
        )

        content = public_path.read_text()
        assert content.startswith("ecdsa-sha2-nistp256 ")

    @pytest.mark.parametrize(
        "bits,curve_name",
        [
            (256, "nistp256"),
            (384, "nistp384"),
            (521, "nistp521"),
        ],
    )
    def test_ecdsa_key_sizes(self, generator, temp_dir, bits, curve_name):
        """Should generate ECDSA keys with correct curves based on bits."""
        _, public_path = generator.generate_key(
            key_type="ecdsa", bits=bits, output_dir=temp_dir, filename=f"test_ecdsa_{bits}"
        )

        content = public_path.read_text()
        assert curve_name in content, f"Expected {curve_name} in public key"

    # ----- Comment Tests -----

    def test_comment_added_to_public_key(self, generator, temp_dir):
        """Comment should be appended to public key."""
        comment = "user@hostname"
        _, public_path = generator.generate_key(
            key_type="ed25519", comment=comment, output_dir=temp_dir, filename="test_comment"
        )

        content = public_path.read_text()
        assert content.endswith(comment)

    def test_empty_comment(self, generator, temp_dir):
        """Empty comment should not add trailing space."""
        _, public_path = generator.generate_key(
            key_type="ed25519", comment="", output_dir=temp_dir, filename="test_no_comment"
        )

        content = public_path.read_text()
        # Should end with base64 characters, not a space
        assert not content.endswith(" ")

    # ----- Passphrase Tests -----

    def test_passphrase_encrypted_key(self, generator, temp_dir):
        """Key with passphrase should be encrypted."""
        private_path, _ = generator.generate_key(
            key_type="ed25519",
            passphrase="secure_passphrase",
            output_dir=temp_dir,
            filename="test_passphrase",
        )

        content = private_path.read_text()
        # Encrypted keys contain ENCRYPTED in the header
        assert "ENCRYPTED" in content

    def test_no_passphrase_unencrypted_key(self, generator, temp_dir):
        """Key without passphrase should not be encrypted."""
        private_path, _ = generator.generate_key(
            key_type="ed25519", passphrase="", output_dir=temp_dir, filename="test_no_passphrase"
        )

        content = private_path.read_text()
        assert "ENCRYPTED" not in content

    # ----- Output Directory Tests -----

    def test_creates_output_directory(self, generator, temp_dir):
        """Should create output directory if it doesn't exist."""
        new_dir = Path(temp_dir) / "subdir" / "nested"
        generator.generate_key(key_type="ed25519", output_dir=str(new_dir), filename="test_nested")

        assert new_dir.exists()

    def test_custom_filename(self, generator, temp_dir):
        """Should use custom filename for key files."""
        filename = "my_custom_key"
        private_path, public_path = generator.generate_key(
            key_type="ed25519", output_dir=temp_dir, filename=filename
        )

        assert private_path.name == f"{filename}.pem"
        assert public_path.name == f"{filename}.pub"

    # ----- Error Handling Tests -----

    def test_invalid_key_type_raises_error(self, generator, temp_dir):
        """Should raise ValueError for invalid key type."""
        with pytest.raises(ValueError, match="Unsupported key type"):
            generator.generate_key(key_type="invalid", output_dir=temp_dir, filename="test_invalid")

    # ----- Fingerprint Tests -----

    def test_get_fingerprint(self, generator, temp_dir):
        """Should return valid SHA256 fingerprint."""
        _, public_path = generator.generate_key(
            key_type="ed25519", output_dir=temp_dir, filename="test_fingerprint"
        )

        fingerprint = generator.get_fingerprint(public_path)
        assert fingerprint.startswith("SHA256:")
        assert len(fingerprint) > 10

    def test_fingerprint_consistency(self, generator, temp_dir):
        """Fingerprint should be consistent for same key."""
        _, public_path = generator.generate_key(
            key_type="ed25519", output_dir=temp_dir, filename="test_consistency"
        )

        fp1 = generator.get_fingerprint(public_path)
        fp2 = generator.get_fingerprint(str(public_path))  # Test with str path

        assert fp1 == fp2

    def test_fingerprint_invalid_format_raises_error(self, generator, temp_dir):
        """Should raise ValueError for invalid public key format."""
        invalid_key_path = Path(temp_dir) / "invalid.pub"
        # Write content with fewer than 2 parts (no space separator)
        invalid_key_path.write_text("invalidkeycontent")

        with pytest.raises(ValueError, match="Invalid public key format"):
            generator.get_fingerprint(invalid_key_path)
