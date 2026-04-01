"""
ARK Server Manager - PyWebView entry point.
Run: python main_web.py  or double-click launch.bat
"""
import sys
import os


def _get_base_dir():
    """Return the directory containing bundled assets (web/, core/, etc.).
    When frozen by PyInstaller --onefile, files are extracted to sys._MEIPASS.
    """
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def main():
    base_dir = _get_base_dir()

    # When frozen the exe lives one level above _MEIPASS; use exe dir as cwd
    # so relative paths in api.py (config, profiles, backups) stay predictable.
    if getattr(sys, "frozen", False):
        work_dir = os.path.dirname(sys.executable)
    else:
        work_dir = base_dir

    os.chdir(work_dir)
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    try:
        import webview
    except ImportError:
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                "pywebview is not installed.\n\nRun:  pip install pywebview",
                "ARK Server Manager — Missing Dependency",
                0x10,  # MB_ICONERROR
            )
        except Exception:
            pass
        sys.exit(1)

    from api import Api
    api = Api()

    html_path = os.path.join(base_dir, "web", "index.html")
    url = f"file:///{html_path.replace(os.sep, '/')}"

    window = webview.create_window(
        title="ARK Server Manager",
        url=url,
        js_api=api,
        width=1300,
        height=840,
        min_size=(960, 640),
        background_color="#1e1e2e",
    )

    webview.start(debug=False)


if __name__ == "__main__":
    main()
