#!/usr/bin/env bash
# Builds a single-file Linux program: dist/TechmiarySales
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --windowed --onefile --name TechmiarySales \
  --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtWebEngineWidgets \
  --exclude-module PySide6.Qt3DCore --exclude-module PySide6.QtQuick --exclude-module PySide6.QtQml \
  main.py
echo "Done: dist/TechmiarySales  (run ./install_linux.sh to add it to your applications menu)"
