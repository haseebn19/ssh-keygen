# -------- IMPORTS --------
import paramiko
from cryptography.hazmat.primitives.asymmetric import ec


# -------- KEY GENERATOR CLASS --------
class SSHKeyManager:
    def generate_keys(self, algorithm: str, bits: int):
        """Generate private key based on the selected algorithm and key length (bits)"""
        match algorithm:
            case "RSA":
                private_key = paramiko.RSAKey.generate(bits)  # Generate RSA key
            case "DSA":
                private_key = paramiko.DSSKey.generate(bits)  # Generate DSA key
            case "ECDSA":
                curve = None
                # Match the curve based on the key length for ECDSA
                match bits:
                    case 256:
                        curve = ec.SECP256R1
                    case 384:
                        curve = ec.SECP384R1
                    case 521:
                        curve = ec.SECP521R1
                    case _:
                        raise ValueError(
                            "The key length you just tried to use does not exist"
                        )
                private_key = paramiko.ECDSAKey.generate(
                    curve=curve
                )  # Generate ECDSA key
            case _:
                raise ValueError(
                    "The generation algorithm you just tried to use does not exist"
                )

        # Create public key from private key
        public_key = f"{private_key.get_name()} {private_key.get_base64()}"

        # Return both public and private keys
        keys = {"public": public_key, "private": private_key}
        return keys

    def save_key(self, key_type, keys, file_path, key_comment=None, passphrase=None):
        """Save the key to a file based on the key type (public or private)"""
        match key_type:
            case "private":
                # Save private key, optionally with a passphrase
                with open(file_path, "w") as file:
                    keys["private"].write_private_key(file, password=passphrase)
            case "public":
                # Save public key, optionally with a comment
                with open(file_path, "w") as file:
                    file.write(f"{keys['public']} {key_comment if key_comment else ''}")
            case _:
                raise ValueError(
                    "The key type you just tried to save as does not exist",
                )
