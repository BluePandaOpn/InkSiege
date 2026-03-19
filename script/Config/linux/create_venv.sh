#!/bin/bash

# Nombre del entorno y ruta según tu estructura
VENV_DIR="./.venv"

# Comprobar si existe, si no, crear de forma discreta
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR" > /dev/null 2>&1
fi

exit 0