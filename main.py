"""
ARK Server Manager — entry point.
Run with: python main.py  or  pythonw main.py (no console window)
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox


def _excepthook(exc_type, exc_value, exc_tb):
    import traceback
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        messagebox.showerror("Unexpected Error", msg)
    except Exception:
        print(msg, file=sys.stderr)


def main():
    sys.excepthook = _excepthook

    # Ensure we run from the project directory so relative imports work
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    root = tk.Tk()
    root.withdraw()  # hide until fully built

    try:
        from ui.app import App
        app = App(root)
    except Exception as e:
        import traceback
        messagebox.showerror("Startup Error",
                              f"Failed to start ARK Server Manager:\n\n{e}\n\n"
                              + traceback.format_exc())
        root.destroy()
        sys.exit(1)

    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()
