import requests
import os
import threading

class SDKUpdater:
    @staticmethod
    def process_update(data, progress_callback):
        """Descarga el archivo real desde la URL proporcionada."""
        url = data['update_url'] if data['update_url'] else data['install_url']
        if not url:
            return False

        try:
            response = requests.get(url, stream=True, timeout=15)
            total_size = int(response.headers.get('content-length', 0))
            
            # Nombre del archivo basado en la URL
            filename = url.split("/")[-1] or "setup.exe"
            
            downloaded = 0
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            # Calcula el porcentaje real para la UI
                            percent = int((downloaded / total_size) * 100)
                            progress_callback(percent)
            return True
        except Exception as e:
            print(f"Error de descarga: {e}")
            return False