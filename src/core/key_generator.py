"""SSH key generation functionality."""

import os
import base64
import hashlib
from pathlib import Path
from typing import Tuple, Literal
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec


class KeyGenerator:
    """SSH key generator that supports various algorithms and configurations."""

    KeyType = Literal["rsa", "ed25519", "ecdsa"]

    def generate_key(
        self,
        key_type: KeyType = "ed25519",
        bits: int = 4096,
        comment: str = "",
        passphrase: str = "",
        output_dir: str = "~/.ssh",
        filename: str = "id_ssh"
    ) -> Tuple[Path, Path]:
        """Generate an SSH key pair using the specified algorithm and parameters."""
        output_dir = Path(output_dir).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)

        if key_type == "rsa":
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=bits)
        elif key_type == "ed25519":
            private_key = ed25519.Ed25519PrivateKey.generate()
        elif key_type == "ecdsa":
            private_key = ec.generate_private_key(ec.SECP256R1())
        else:
            raise ValueError(f"Unsupported key type: '{key_type}'")

        private_key_path = output_dir / f"{filename}.pem"
        encryption_algorithm = (
            serialization.BestAvailableEncryption(passphrase.encode())
            if passphrase else serialization.NoEncryption()
        )

        with private_key_path.open("wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption_algorithm
            ))

        if os.name == 'posix':
            os.chmod(private_key_path, 0o600)

        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        )
        public_key_str = public_key_bytes.decode("utf-8")
        if comment:
            public_key_str += f" {comment}"

        public_key_path = output_dir / f"{filename}.pub"
        with public_key_path.open("w", encoding="utf-8") as f:
            f.write(public_key_str)

        return private_key_path, public_key_path

    def get_fingerprint(self, public_key_path: str) -> str:
        """Get the fingerprint of a public key."""
        path = Path(public_key_path).expanduser()
        with path.open("r", encoding="utf-8") as f:
            key_data = f.read().strip()

        key_parts = key_data.split(" ")
        if len(key_parts) < 2:
            raise ValueError("Invalid public key format")

        key_bytes = base64.b64decode(key_parts[1])
        fp_hash = hashlib.sha256(key_bytes).digest()
        fp_base64 = base64.b64encode(fp_hash).decode("utf-8").rstrip("=")

        return f"SHA256:{fp_base64}"
