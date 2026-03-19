import requests
import os
from interpreter import SDKInterpreter
from security import SecurityManager
from updater import SDKUpdater
from gui import SDKGui

URL = "https://raw.githubusercontent.com/BluePandaOpn/InkSiege/refs/heads/main/script/version/SDK.version"

def installation_worker(version_data, progress_fn):
    # 1. Determinar si es instalación limpia (.exe) o parche (.zip)
    # Por ahora simularemos que bajamos el update .zip
    update_url = version_data['update_url']
    
    if not update_url:
        # Si no hay URL, simulamos progreso para pruebas
        for i in range(101):
            import time
            time.sleep(0.02)
            progress_fn(i)
    else:
        # Descarga real y descompresión
        SDKUpdater.download_and_extract(update_url, "./game_files", progress_fn)
    
    # Guardar versión local y Seguridad
    with open("current_version.txt", "w") as f: f.write(version_data['v'])
    # (Opcional) SecurityManager.save_hash(...)

def main():
    try:
        r = requests.get(URL, timeout=10)
        r.raise_for_status()
        
        parser = SDKInterpreter(r.text)
        versions = parser.get_versions()
        
        app = SDKGui(versions, installation_worker)
        app.mainloop()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()