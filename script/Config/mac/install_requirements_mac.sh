#!/bin/bash
VENV_PYTHON="./.venv/bin/python3"
REQ_FILE="requirements.txt"

if [ ! -f "$VENV_PYTHON" ]; then
    exit 1
fi

# Instalar de forma silenciosa
$VENV_PYTHON -m pip install --upgrade pip --quiet
if [ -f "$REQ_FILE" ]; then
    $VENV_PYTHON -m pip install -r "$REQ_FILE" --quiet
else
    $VENV_PYTHON -m pip install pygame imageio --quiet
fi
exit 0