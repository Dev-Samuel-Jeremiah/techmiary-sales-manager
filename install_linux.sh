#!/usr/bin/env bash
# Installs the built program for the current user and adds it to the applications menu.
set -e
cd "$(dirname "$0")"
BIN="dist/TechmiarySales"
[ -f "$BIN" ] || BIN="TechmiarySales"
mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications" "$HOME/.local/share/icons"
cp "$BIN" "$HOME/.local/bin/TechmiarySales"
chmod +x "$HOME/.local/bin/TechmiarySales"
cp assets/techmiary.png "$HOME/.local/share/icons/techmiary-sales.png"
cat > "$HOME/.local/share/applications/techmiary-sales.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Techmiary Sales Manager
Comment=Record services and see daily and monthly sales
Exec=$HOME/.local/bin/TechmiarySales
Icon=$HOME/.local/share/icons/techmiary-sales.png
Categories=Office;Finance;
Terminal=false
EOF
echo "Installed. Find 'Techmiary Sales Manager' in your applications menu."
