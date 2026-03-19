# Configuración
$VENV_PATH = ".\.venv\Scripts\python.exe"
$REQ_FILE = "requirements.txt"

# Silenciar errores no críticos
$ErrorActionPreference = "SilentlyContinue"

# 1. Verificar si existe el entorno virtual
if (!(Test-Path $VENV_PATH)) {
    # Si no existe el venv, no podemos instalar nada discretamente
    exit 1
}

# 2. Verificar si existe el archivo de requisitos
if (Test-Path $REQ_FILE) {
    # Ejecutar instalación de forma silenciosa (--quiet)
    # El operador & ejecuta el comando
    & $VENV_PATH -m pip install --upgrade pip --quiet
    & $VENV_PATH -m pip install -r $REQ_FILE --quiet
} else {
    # Si no hay requirements.txt, instalamos las básicas del proyecto InkSiege
    & $VENV_PATH -m pip install pygame imageio --quiet
}

exit 0