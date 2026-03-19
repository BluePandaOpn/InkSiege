# Definir nombre del entorno
$VENV_NAME = ".venv"

# Redirigir errores a la nulidad para máxima discreción
$ErrorActionPreference = "SilentlyContinue"

# Comprobar si ya existe el entorno virtual
if (!(Test-Path -Path ".\$VENV_NAME")) {
    # Si no existe, se crea de forma silenciosa
    # --without-pip se puede quitar si necesitas pip de inmediato, 
    # pero para creación pura es más rápido.
    python -m venv $VENV_NAME
    
    # Opcional: Ocultar la carpeta en Windows para que sea "discreta" visualmente
    (Get-Item ".\$VENV_NAME").Attributes = 'Hidden'
}

# Finalización limpia y sin salida de texto
exit 0