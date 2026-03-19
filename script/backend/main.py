import requests
import os
from interpreter import SDKInterpreter
from security import SecurityManager
from gui import InkSiegeLauncher

# Configuración del Proyecto
SDK_URL = "https://raw.githubusercontent.com/BluePandaOpn/InkSiege/refs/heads/main/script/version/SDK.version"
LOCAL_VERSION_FILE = "current_sdk.txt"
HASH_CONTROL_FILE = ".sdk_lock"

def process_installation(version_name):
    """Lógica para aplicar la versión seleccionada."""
    # Guardar la versión
    with open(LOCAL_VERSION_FILE, "w") as f:
        f.write(version_name)
    
    # Crear sello de seguridad
    new_hash = SecurityManager.calculate_hash(LOCAL_VERSION_FILE)
    with open(HASH_CONTROL_FILE, "w") as f:
        f.write(new_hash)
    
    print(f"Instalación de {version_name} finalizada con éxito.")

def main():
    print("Conectando con InkSiege GitHub...")
    try:
        response = requests.get(SDK_URL, timeout=10)
        response.raise_for_status()
        
        # 1. Interpretar archivo
        interpreter = SDKInterpreter(response.text)
        available_versions = interpreter.get_all_versions()
        
        if not available_versions:
            print("No se encontraron etiquetas [SDK] válidas.")
            return

        # 2. Verificar integridad local antes de abrir
        if os.path.exists(LOCAL_VERSION_FILE) and os.path.exists(HASH_CONTROL_FILE):
            with open(HASH_CONTROL_FILE, "r") as hf:
                if not SecurityManager.verify(LOCAL_VERSION_FILE, hf.read().strip()):
                    print("¡ADVERTENCIA! El archivo de versión local fue modificado ilegalmente.")

        # 3. Lanzar GUI
        app = InkSiegeLauncher(available_versions, process_installation)
        app.mainloop()

    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    main()