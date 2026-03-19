import requests
import customtkinter as ctk
from interpreter import SDKInterpreter
from updater import SDKUpdater
from gui import InkSiegeLauncher

URL_SDK = "https://raw.githubusercontent.com/BluePandaOpn/InkSiege/refs/heads/main/script/version/SDK.version"
URL_SDL = "https://raw.githubusercontent.com/BluePandaOpn/InkSiege/refs/heads/main/script/version/SDL.install"

def main():
    try:
        # Usamos un timeout para evitar que el programa se quede colgado
        sdk_res = requests.get(URL_SDK, timeout=10).text
        sdl_res = requests.get(URL_SDL, timeout=10).text
        
        interpreter = SDKInterpreter(sdk_res, sdl_res)
        data = interpreter.get_combined_data()
        
        if not data:
            raise ValueError("No se pudieron parsear los datos de las versiones.")

        app = InkSiegeLauncher(data, SDKUpdater.process_update)
        app.mainloop()
        
    except Exception as e:
        # En una app profesional, esto debería ir a un log
        print(f"Error Crítico: {e}")
        root = ctk.CTk()
        root.withdraw()
        messagebox.showerror("Error de Conexión", f"No se pudo conectar con el servidor de InkSiege:\n{e}")

if __name__ == "__main__":
    main()