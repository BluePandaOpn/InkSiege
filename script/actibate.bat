@echo off
setlocal
title InkSiege Launcher - BluePanda Studios

:: Configuración de colores (Opcional: Fondo negro, texto verde)
color 0A

echo ======================================================
echo           INICIANDO INKSIEGE V0.1.5
echo ======================================================

:: 1. Verificar si existe la carpeta del entorno virtual (.venv)
if not exist ".venv" (
    echo [!] No se detecto el entorno virtual. Creando uno nuevo...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno. Revisa si Python esta instalado.
        pause
        exit /b
    )
    echo [OK] Entorno creado exitosamente.
)

:: 2. Activar el entorno virtual
echo [+] Activando entorno virtual...
call .venv\Scripts\activate

:: 3. Verificar e instalar dependencias usando requirements.txt
if exist "requirements.txt" (
    echo [+] Verificando dependencias...
    :: Compara lo instalado con el txt para no perder tiempo si ya esta todo
    pip install -r requirements.txt --quiet
    echo [OK] Dependencias al dia.
) else (
    echo [!] No se encontro requirements.txt. Instalando paquetes base...
    pip install pygame imageio --quiet
)

:: 4. Limpiar basura de Python (Opcional, mantiene el proyecto limpio)
echo [+] Limpiando cache...
if exist "__pycache__" rd /s /q "__pycache__"

:: 5. Ejecutar el juego
echo ======================================================
echo           ¡A JUGAR! - CERRAR PARA SALIR
echo ======================================================
python ../main.py

:: 6. Al cerrar el juego
echo.
echo [INFO] El juego se ha cerrado.
call deactivate
pause