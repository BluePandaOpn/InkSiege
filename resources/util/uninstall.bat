@echo off
set "target_dir=C:\Program Files\InkSiege"

:: --- BLOQUE DE AUTO-ELEVACIÓN ---
:: Verifica si tenemos permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process -FilePath '%0' -Verb RunAs"
    exit /b
)

:: --- INICIO DEL TRABAJO ---
title Limpiador InkSiege
echo Ejecutando con privilegios de sistema...

if exist "%target_dir%" (
    echo Eliminando contenido de: %target_dir%
    
    :: Borrar archivos
    del /q /s /f "%target_dir%\*.*"
    
    :: Borrar subcarpetas
    for /d %%p in ("%target_dir%\*") do rd /s /q "%%p"
    
    echo.
    echo [OK] El contenido ha sido eliminado.
) else (
    echo [ERROR] La carpeta no existe.
)

