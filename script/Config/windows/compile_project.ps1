# compile_project.ps1 - Compilador para InkSiege
# Configuración de rutas según tu estructura
$PROJECT_NAME = "InkSiege"
$PYTHON_VENV = ".\.venv\Scripts\python.exe" # Ajustado a la raíz o cambia a .\script\.venv\...
$MAIN_FILE = "main.py"
$ICON_FILE = "resources/assets/logo/logo.ico"

# 1. Verificar si PyInstaller está instalado en el venv
Write-Host "--- Iniciando Proceso de Compilación ---" -ForegroundColor Cyan
& $PYTHON_VENV -m pip install pyinstaller --quiet

# 2. Limpiar compilaciones anteriores para evitar conflictos
if (Test-Path "./dist") { Remove-Item -Recurse -Force "./dist" }
if (Test-Path "./build") { Remove-Item -Recurse -Force "./build" }

Write-Host "Compilando en modo Directorio (--onedir)..." -ForegroundColor Yellow

# 3. Ejecución de PyInstaller
# --onedir: Crea una carpeta con el exe y las librerías (más estable)
# --windowed: No abre una consola negra al iniciar el juego
# --add-data: Incluye la carpeta resources completa manteniendo la estructura
& $PYTHON_VENV -m PyInstaller --noconfirm --onedir --windowed `
    --name "$PROJECT_NAME" `
    --icon "$ICON_FILE" `
    --add-data "resources;resources" `
    --add-data "bluepanda.py;." `
    "$MAIN_FILE"

# 4. Verificación final
if (Test-Path "./dist/$PROJECT_NAME") {
    Write-Host "`n[ÉXITO] Proyecto compilado en: ./dist/$PROJECT_NAME" -ForegroundColor Green
    Write-Host "Puedes enviar esa carpeta completa a tus jugadores." -ForegroundColor White
} else {
    Write-Host "`n[ERROR] Hubo un problema durante la compilación." -ForegroundColor Red
}

pause