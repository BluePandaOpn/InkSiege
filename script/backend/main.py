import requests
from interpreter import SDKInterpreter
from updater import SDKUpdater
from gui import InkSiegeLauncher

# URLs de tus archivos en GitHub
URL_SDK = "https://raw.githubusercontent.com/BluePandaOpn/InkSiege/refs/heads/main/script/version/SDK.version"
URL_SDL = "https://raw.githubusercontent.com/BluePandaOpn/InkSiege/refs/heads/main/script/version/SDL.install"

def main():
    try:
        print("Obteniendo manifiestos...")
        sdk_res = requests.get(URL_SDK).text
        sdl_res = requests.get(URL_SDL).text
        
        # Procesar ambos archivos
        interpreter = SDKInterpreter(sdk_res, sdl_res)
        combined_data = interpreter.get_combined_data()
        
        # Lanzar Launcher
        app = InkSiegeLauncher(combined_data, SDKUpdater.process_update)
        app.mainloop()
        
    except Exception as e:
        print(f"Error crítico de conexión: {e}")

if __name__ == "__main__":
    main()