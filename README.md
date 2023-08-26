# SSH Key Generator

![SSH Key Generator Logo](logo.png)

SSH Key Generator is an application designed to simplify the process of generating SSH keys. Built with Python and Tkinter, this application provides a user-friendly interface for generating SSH keys with different algorithms and key lengths. It's a simple solution for creating, viewing, and saving SSH keys.

## Features

- **Algorithm Selection**: Choose from a variety of algorithms like RSA, DSA, and ECDSA for key generation.
  
- **Key Length Options**: Customize the key length in bits based on the selected algorithm.
  
- **Generate Keys**: Generate SSH keys with a single click.
  
- **Public Key Display**: View the generated public key within the application.
  
- **Comment and Passphrase**: Add an optional comment and passphrase for the generated keys.
  
- **Save Keys**: Save the generated public and private keys to your local storage.

## Prerequisites

- Python 3.11
- `paramiko` library
- `tkinter` for GUI
- `json` for configuration management

## Installation

1. Clone the repository:
   ```powershell
   git clone https://github.com/haseebn19/ssh-keygen.git
   ```

2. Navigate to the project directory:
   ```powershell
   cd ssh-keygen
   ```

3. Install the required dependencies:
   ```powershell
   pip3.11 install -r requirements.txt
   ```

4. Run the application:
   ```powershell
   py -3.11 main.py
   ```

## Usage

1. Select the algorithm and key length from the dropdown menus.
  
2. Optionally, add a comment and passphrase.
  
3. Click the "Generate Keys" button to generate the keys.
  
4. View the generated public key and save both keys if needed.

## Contributing

If you'd like to contribute to my SSH Key Generator or have suggestions for improvements, feel free to fork the repository and submit a pull request.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
