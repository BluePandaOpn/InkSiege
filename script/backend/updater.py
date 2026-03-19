import zipfile
import requests
import os
import io

class SDKUpdater:
    @staticmethod
    def download_and_extract(url, target_path, progress_callback):
        if not url: return False
        
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        if response.status_code == 200:
            bytes_downloaded = 0
            zip_data = io.BytesIO()
            
            for chunk in response.iter_content(chunk_size=4096):
                zip_data.write(chunk)
                bytes_downloaded += len(chunk)
                # Calcular progreso (0 a 100)
                percent = (bytes_downloaded / total_size) * 100
                progress_callback(percent)

            # Descomprimir
            with zipfile.ZipFile(zip_data) as zip_ref:
                zip_ref.extractall(target_path)
            return True
        return False