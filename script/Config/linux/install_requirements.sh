#!/bin/bash

VENV_PYTHON="./.venv/bin/python3"
REQ_FILE="requirements.txt"

# Verificar si el venv existe
if [ ! -f "$VENV_PYTHON" ]; then
    exit 1
fi

# Instalar dependencias de forma silenciosa
if [ -f "$REQ_FILE" ]; then
    $VENV_PYTHON -m pip install --upgrade pip --quiet
    $VENV_PYTHON -m pip install -r "$REQ_FILE" --quiet
else
    # Instalación manual si no hay txt
    $VENV_PYTHON -m pip install pygame imageio --quiet
fi

exit 0