#!/bin/bash

PROJECT_NAME="InkSiege_Linux"
VENV_PYTHON="./.venv/bin/python3"
MAIN_FILE="main.py"

echo "--- Iniciando Compilación para Linux ---"

# Asegurar que PyInstaller esté presente
$VENV_PYTHON -m pip install pyinstaller --quiet

# Limpiar carpetas previas
rm -rf ./dist ./build

# Compilar
# Nota: En Linux el separador de --add-data es ":" (dos puntos), no ";"
$VENV_PYTHON -m PyInstaller --noconfirm --onedir --windowed \
    --name "$PROJECT_NAME" \
    --add-data "resources:resources" \
    --add-data "bluepanda.py:." \
    "$MAIN_FILE"

if [ -d "./dist/$PROJECT_NAME" ]; then
    echo -e "\n[ÉXITO] Compilado en: ./dist/$PROJECT_NAME"
else
    echo -e "\n[ERROR] Falló la compilación."
fi