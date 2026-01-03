from gui import App
import tkinter as tk
from tkinter import messagebox

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        # If the app fails to start (e.g., config error), show a popup before crashing
        # Temporary root window to show the error
        root = tk.Tk()
        root.withdraw() # Hide the main window
        messagebox.showerror("Critical Error", f"Application failed to start:\n{e}")
        print(f"CRITICAL ERROR: {e}")