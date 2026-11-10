@echo off
REM Builds TechmiarySales.exe on Windows. Needs Python 3.10+ from python.org (tick "Add python.exe to PATH").
cd /d "%~dp0"
echo Installing build tools...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
echo Building...
python -m PyInstaller --noconfirm --clean --windowed --onefile ^
  --name TechmiarySales --icon assets\techmiary.ico ^
  --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtWebEngineWidgets ^
  --exclude-module PySide6.Qt3DCore --exclude-module PySide6.QtQuick --exclude-module PySide6.QtQml ^
  main.py
echo.
echo Done. Your program is in the "dist" folder: dist\TechmiarySales.exe
echo Copy it anywhere (e.g. the Desktop) and double-click to run.
pause
