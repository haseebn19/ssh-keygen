# SSH Key Generator

[![CI](https://github.com/haseebn19/ssh-keygen/actions/workflows/ci.yml/badge.svg)](https://github.com/haseebn19/ssh-keygen/actions/workflows/ci.yml)

<img src="resources/logo.svg" alt="SSH Key Generator Logo" width="250">

A desktop application for generating SSH keys with a user-friendly interface.

## Screenshots

<img src="resources/screenshot-window.png" alt="Main Window" width="500">

<img src="resources/screenshot-generated.png" alt="Generated Output" width="500">

## Features

- **Multiple Algorithms**: ED25519, RSA, and ECDSA key support
- **Key Size Options**: 2048-4096 for RSA, 256/384/521 for ECDSA
- **Passphrase Protection**: Optional encryption for private keys
- **Fingerprint Display**: SHA256 fingerprint generation
- **Quick Copy**: One-click copy for public key and fingerprint
- **Dark/Light Theme**: Automatic theme detection

## Prerequisites

- Python 3.11+

## Installation

```bash
git clone https://github.com/haseebn19/ssh-keygen.git
cd ssh-keygen
python -m venv .venv

# Windows
.\.venv\Scripts\Activate

# Linux/macOS
source .venv/bin/activate

pip install -e .
```

## Usage

```bash
python -m src.main
```

1. Select the algorithm and key size
2. Optionally enter a comment and passphrase
3. Choose the output location or use the default (`~/.ssh`)
4. Click "Generate SSH Key"
5. Copy the public key or open the file location

## Development

### Setup

```bash
pip install -e ".[dev]"
```

### Testing

```bash
pytest
```

With coverage:

```bash
pytest --cov=src
```

### Linting

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Building

Create a standalone executable:

```bash
pyinstaller main.spec
```

The `.exe` will be in the `dist/` folder.

## Project Structure

```
ssh-keygen/
├── src/
│   ├── main.py               # Entry point
│   ├── utils.py              # Utilities
│   ├── core/
│   │   └── key_generator.py  # Key generation logic
│   └── ui/
│       └── main_window.py    # PyQt6 interface
├── tests/                    # Test suite
├── resources/                # Icons
├── pyproject.toml            # Project config
└── main.spec                 # PyInstaller config
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Credits

- [cryptography](https://cryptography.io/) - Key generation
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - User interface

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
