#!/bin/bash
# Script discreto para macOS
VENV_DIR="./.venv"

if [ ! -d "$VENV_DIR" ]; then
    # Intentar usar python3 (estándar en macOS)
    python3 -m venv "$VENV_DIR" > /dev/null 2>&1
fi
exit 0