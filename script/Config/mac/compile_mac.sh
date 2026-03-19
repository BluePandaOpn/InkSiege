#!/bin/bash

PROJECT_NAME="InkSiege"
VENV_PYTHON="./.venv/bin/python3"
MAIN_FILE="main.py"
# Ruta al icono (macOS prefiere .icns, pero PyInstaller puede convertir el .png)
ICON_FILE="resources/assets/logo/logo.png"

echo "--- Compilando para macOS ---"

# Instalar PyInstaller si no existe
$VENV_PYTHON -m pip install pyinstaller --quiet

# Limpiar restos
rm -rf ./dist ./build

# Compilar
# --windowed: En macOS es obligatorio para crear el .app
# --add-data: El separador en macOS también es ":"
$VENV_PYTHON -m PyInstaller --noconfirm --onedir --windowed \
    --name "$PROJECT_NAME" \
    --icon "$ICON_FILE" \
    --add-data "resources:resources" \
    --add-data "bluepanda.py:." \
    "$MAIN_FILE"

if [ -d "./dist/$PROJECT_NAME.app" ]; then
    echo -e "\n[OK] Aplicación creada: ./dist/$PROJECT_NAME.app"
    echo "Sugerencia: Comprime la carpeta .app en un .zip para compartirla."
else
    echo -e "\n[ERROR] No se pudo crear el paquete .app"
fi