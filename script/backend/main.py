import os
from updater import AppUpdater
from interpreter import SDKInterpreter
from security import SecurityManager
from gui import SDKLauncher

GITHUB_URL = "https://raw.githubusercontent.com/USUARIO/REPO/main/versiones.txt"
VERSION_FILE = "version_local.txt"
HASH_FILE = ".hash_seguridad"

def install_version(version_name):
    """Esta función se ejecuta cuando el usuario pulsa el botón en la GUI."""
    print(f"[*] Procesando instalación de {version_name}...")
    
    # 1. Guardar la versión en el archivo local
    with open(VERSION_FILE, "w") as f:
        f.write(version_name)
    
    # 2. Generar nueva firma de seguridad para evitar desconfiguración
    new_hash = SecurityManager.calculate_hash(VERSION_FILE)
    with open(HASH_FILE, "w") as f:
        f.write(new_hash)
    
    print(f"[OK] Sistema configurado en versión: {version_name}")
    # Aquí podrías disparar la descarga de archivos reales de esa versión

def main():
    # Descargar manifiesto de versiones
    updater = AppUpdater(GITHUB_URL)
    content = updater.download_manifest()

    if not content:
        print("Error crítico: No se pudo conectar a GitHub.")
        return

    # Interpretar versiones disponibles
    parser = SDKInterpreter(content)
    available_versions = parser.get_all_versions()

    if not available_versions:
        print("No se encontraron versiones válidas en el archivo SDK.")
        return

    # Lanzar Interfaz Gráfica con la lista de versiones
    app = SDKLauncher(available_versions, install_version)
    app.mainloop()

if __name__ == "__main__":
    main()