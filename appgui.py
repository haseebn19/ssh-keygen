# -------- IMPORTS --------
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from keygen import SSHKeyManager


# -------- GUI CLASS --------
class SSHKeyGeneratorApp:
    def __init__(self, root):
        # Load configuration from JSON file
        with open("config.json", "r") as file:
            self.config = json.load(file)

        # Initialize main window properties
        self.root = root
        self.root.title(self.config["title"])
        self.root.iconbitmap(self.config["icon"])
        self.root.minsize(*self.config["min_size"])
        self.root.geometry(self.config["geometry"])
        self.keys = {
            "private": None,
            "public": None,
        }
        self.key_manager = SSHKeyManager()
        self.build_gui()  # Build the GUI components

    def build_gui(self):
        """Build the main GUI components."""
        # Main frame
        self.main_frame = tk.Frame(
            self.root,
            bd=2,
            relief=tk.GROOVE,
        )
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        # Build GUI components
        self.build_algorithm_options()  # Algorithm selection
        self.build_key_length_options()  # Key length selection
        self.build_generate_button()  # Generate keys button
        self.build_public_key_display()  # Public key display
        self.build_key_comment_entry()  # Comment entry
        self.build_passphrase_entry()  # Passphrase entry
        self.build_save_buttons()  # Save buttons

    def build_algorithm_options(self):
        """Build the algorithm options (RSA, DSA, ECDSA)."""
        self.algorithm_bits_options = self.config["algorithm_bits_options"]
        self.algorithm_frame = tk.Frame(self.main_frame)
        self.algorithm_frame.pack(anchor=tk.W)
        self.algorithm_label = tk.Label(
            self.algorithm_frame,
            text="Algorithm:",
        )
        self.algorithm_label.pack(side=tk.LEFT)
        self.algorithm_var = tk.StringVar(value="RSA")
        self.algorithm_var.trace("w", self.update_bits_options)
        self.algorithm_option = tk.OptionMenu(
            self.algorithm_frame,
            self.algorithm_var,
            *self.algorithm_bits_options.keys(),
        )
        self.algorithm_option.pack(side=tk.LEFT)

    def build_key_length_options(self):
        """Build the key length options (bits)."""
        self.bits_frame = tk.Frame(self.main_frame)
        self.bits_frame.pack(anchor=tk.W)
        self.bits_label = tk.Label(
            self.bits_frame,
            text="Key Length (bits):",
        )
        self.bits_label.pack(side=tk.LEFT)
        self.bits_var = tk.StringVar()
        self.bits_option = tk.OptionMenu(self.bits_frame, self.bits_var, "")
        self.bits_option.pack(side=tk.LEFT)
        self.update_bits_options()  # Update key length options based on algorithm

    def build_generate_button(self):
        """Build the generate keys button."""
        self.generate_button = tk.Button(
            self.main_frame,
            text="Generate Keys",
            command=self.generate,
        )
        self.generate_button.pack(pady=10)

    def build_public_key_display(self):
        """Build the public key display area."""
        self.public_key_label = tk.Label(
            self.main_frame,
            text="Public Key:",
        )
        self.public_key_label.pack()
        self.public_key_text = tk.Text(
            self.main_frame,
            height=6,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=self.root["bg"],
        )
        self.public_key_text.pack(padx=5, fill=tk.BOTH, expand=True)

    def build_key_comment_entry(self):
        """Build the comment entry area."""
        self.key_comment_label = tk.Label(
            self.main_frame,
            text="Comment:",
        )
        self.key_comment_label.pack()
        self.key_comment_text = tk.Text(
            self.main_frame,
            height=2,
            wrap=tk.WORD,
            state="normal",
        )
        self.key_comment_text.pack(padx=5, fill=tk.BOTH, expand=True)
        self.key_comment_text.bind("<KeyRelease>", self.update_key_comment)

    def build_passphrase_entry(self):
        """Build the passphrase entry area."""
        self.passphrase_label = tk.Label(
            self.main_frame,
            text="Passphrase:",
        )
        self.passphrase_label.pack()
        self.passphrase_entry = tk.Entry(
            self.main_frame,
            show="*",
        )
        self.passphrase_entry.pack(padx=5, fill=tk.BOTH)

    def build_save_buttons(self):
        """Build the save buttons for public and private keys."""
        self.save_buttons_frame = tk.Frame(self.main_frame)
        self.save_buttons_frame.pack(pady=10)
        self.save_public_button = tk.Button(
            self.save_buttons_frame,
            text="Save Public Key",
            command=lambda: self.save(key_type="public"),
            state=tk.DISABLED,
        )
        self.save_public_button.pack(side=tk.LEFT)
        self.save_private_button = tk.Button(
            self.save_buttons_frame,
            text="Save Private Key",
            command=lambda: self.save(key_type="private"),
            state=tk.DISABLED,
        )
        self.save_private_button.pack(side=tk.LEFT)

    def update_bits_options(self, *args):
        """Update key length options based on selected algorithm."""
        bits_menu = self.bits_option["menu"]
        bits_menu.delete(0, tk.END)
        for bit_option in self.algorithm_bits_options[self.algorithm_var.get()]:
            bits_menu.add_command(
                label=bit_option,
                command=lambda value=bit_option: self.bits_var.set(value),
            )
        self.bits_var.set(self.algorithm_bits_options[self.algorithm_var.get()][0])

    def update_text_widget(self, widget: tk.Text, text: str, state=tk.DISABLED):
        """Update the content of a text widget."""
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)
        widget.config(state=state)

    def update_key_comment(self, event):
        """Update public key display with comment."""
        if self.keys["public"]:
            key_comment = self.key_comment_text.get(1.0, tk.END).strip()
            public_key_with_comment = (
                f"{self.keys['public']} {key_comment if key_comment else ''}"
            )
            self.update_text_widget(self.public_key_text, public_key_with_comment)

    def generate(self):
        """Generate keys based on selected algorithm and bits."""
        try:
            algorithm = self.algorithm_var.get()
            bits = int(self.bits_var.get())
            self.keys = self.key_manager.generate_keys(algorithm, bits)
            key_comment = self.key_comment_text.get(1.0, tk.END).strip()
            public_key_with_comment = (
                self.keys["public"] + " " + key_comment
                if key_comment
                else self.keys["public"]
            )
            self.update_text_widget(self.public_key_text, public_key_with_comment)
            self.save_public_button.config(state=tk.NORMAL)
            self.save_private_button.config(state=tk.NORMAL)
        except ValueError as error:
            messagebox.showerror(title=self.config["title"], message=error)

    def save(self, key_type="public"):
        """Save keys to file"""

        # Define default filename and extension based on key type
        default_filename = f"{key_type}_key"
        default_extension = ".txt" if key_type == "public" else ".pem"
        filetypes = (
            [("PEM files", "*.pem")]
            if key_type == "private"
            else [("Text files", "*.txt")]
        )

        # Prompt user to select save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=default_extension,
            initialfile=default_filename,
            filetypes=filetypes,
        )
        if not file_path:
            return

        # Retrieve comment and passphrase
        key_comment = self.key_comment_text.get(1.0, tk.END).strip()
        passphrase = self.passphrase_entry.get() or None

        try:
            self.key_manager.save_key(
                key_type, self.keys, file_path, key_comment, passphrase
            )
            messagebox.showinfo(
                title=self.config["title"], message="File sucessfully saved"
            )
        except ValueError as error:
            messagebox.showerror(title=self.config["title"], message=error)
