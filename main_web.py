"""
ARK Server Manager - PyWebView entry point.
Run: python main_web.py  or double-click launch.bat
"""
import sys
import os

def main():
    # Ensure imports work from project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    try:
        import webview
    except ImportError:
        print("pywebview not installed. Run: pip install pywebview")
        input("Press Enter to exit...")
        sys.exit(1)

    from api import Api
    api = Api()

    html_path = os.path.join(script_dir, "web", "index.html")
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
