# -------- IMPORTS --------
import tkinter as tk
from appgui import SSHKeyGeneratorApp

# -------- APPLICATION --------
if __name__ == "__main__":
    root = tk.Tk()
    app = SSHKeyGeneratorApp(root)
    root.mainloop()
