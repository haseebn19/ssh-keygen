"""SSH key generation."""

import base64
import hashlib
import os
from pathlib import Path
from typing import ClassVar, Literal

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa


class KeyGenerator:
    """Generates SSH key pairs with various algorithms."""

    KeyType = Literal["rsa", "ed25519", "ecdsa"]

    ECDSA_CURVES: ClassVar[dict[int, ec.EllipticCurve]] = {
        256: ec.SECP256R1(),
        384: ec.SECP384R1(),
        521: ec.SECP521R1(),
    }

    @staticmethod
    def key_paths(output_dir: str | Path, filename: str) -> tuple[Path, Path]:
        """Return the private and public key paths for a base filename."""
        directory = Path(output_dir).expanduser()
        return directory / f"{filename}.pem", directory / f"{filename}.pub"

    def generate_key(
        self,
        key_type: KeyType = "ed25519",
        bits: int = 4096,
        comment: str = "",
        passphrase: str = "",
        output_dir: str = "~/.ssh",
        filename: str = "id_ssh",
        overwrite: bool = False,
    ) -> tuple[Path, Path]:
        """Generate an SSH key pair and save it as <filename>.pem and <filename>.pub.

        Raises FileExistsError if either file exists, unless overwrite is True.
        """
        private_key_path, public_key_path = self.key_paths(output_dir, filename)
        if not overwrite:
            for path in (private_key_path, public_key_path):
                if path.exists():
                    raise FileExistsError(f"Key file already exists: {path}")
        private_key_path.parent.mkdir(parents=True, exist_ok=True)

        if key_type == "rsa":
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=bits)
        elif key_type == "ed25519":
            private_key = ed25519.Ed25519PrivateKey.generate()
        elif key_type == "ecdsa":
            if bits not in self.ECDSA_CURVES:
                raise ValueError(f"Unsupported ECDSA key size: {bits}")
            private_key = ec.generate_private_key(self.ECDSA_CURVES[bits])
        else:
            raise ValueError(f"Unsupported key type: '{key_type}'")

        encryption = (
            serialization.BestAvailableEncryption(passphrase.encode())
            if passphrase
            else serialization.NoEncryption()
        )

        # Create the private key readable by its owner only, so no other user can read it
        # before the permissions are set. Windows ignores this mode.
        descriptor = os.open(private_key_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=encryption,
                )
            )

        if os.name == "posix":
            # A replaced key file keeps its old mode, so set it again
            private_key_path.chmod(0o600)

        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH, format=serialization.PublicFormat.OpenSSH
        )
        public_key_line = public_key_bytes.decode("utf-8")
        if comment:
            public_key_line += f" {comment}"
        public_key_path.write_text(public_key_line + "\n", encoding="utf-8")

        return private_key_path, public_key_path

    def get_fingerprint(self, public_key_path: str | Path) -> str:
        """Return the SHA256 fingerprint of a public key, as `ssh-keygen -l` shows it."""
        key_data = Path(public_key_path).expanduser().read_text(encoding="utf-8").strip()

        key_parts = key_data.split(" ")
        if len(key_parts) < 2:
            raise ValueError("Invalid public key format")

        key_bytes = base64.b64decode(key_parts[1])
        fp_hash = hashlib.sha256(key_bytes).digest()
        fp_base64 = base64.b64encode(fp_hash).decode("utf-8").rstrip("=")

        return f"SHA256:{fp_base64}"
