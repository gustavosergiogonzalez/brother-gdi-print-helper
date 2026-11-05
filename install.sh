#!/bin/bash
set -e
echo "👦� Instalando Brother HLM1200 Print Helper..."
BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
mkdir -p "$BIN_DIR"
mkdir -p "$APP_DIR"
cp src/imprimir_gui.py "$BIN_DIR/imprimir_gui.py"
chmod +x "$BIN_DIR/imprimir_gui.py"
cp desktop/imprimir_hl1200.desktop "$APP_DIR/imprimir_hl1200.desktop"
echo "✅ Instalado con éxito."
