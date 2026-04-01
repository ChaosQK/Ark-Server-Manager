@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo  ARK Server Manager - Build Script
echo ============================================
echo.

echo [1/3] Installing PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller. Make sure Python 3.10+ is in PATH.
    pause & exit /b 1
)

echo [2/3] Building ArkServerManager.exe ^(this may take a few minutes^)...
pyinstaller --onefile --windowed ^
  --name "ArkServerManager" ^
  --add-data "web;web" ^
  --hidden-import "webview.platforms.winforms" ^
  --hidden-import "webview.platforms.edgechromium" ^
  --collect-all webview ^
  main_web.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed. See output above for details.
    pause & exit /b 1
)

echo.
echo [3/3] Build complete!
echo.
echo Output: dist\ArkServerManager.exe
echo.
echo NOTE: Microsoft Edge WebView2 Runtime must be installed on the target machine.
echo       Download: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
echo.
pause
