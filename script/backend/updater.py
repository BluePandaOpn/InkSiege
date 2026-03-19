import webbrowser
import os
import time

class SDKUpdater:
    @staticmethod
    def process_update(data, progress_callback):
        """Simula la preparación y abre el link de descarga."""
        progress_callback(10)
        time.sleep(0.5)
        
        # Priorizar update_url si ya existe una versión local, si no install_url
        url_to_open = data['update_url'] if data['update_url'] else data['install_url']
        
        if url_to_open:
            progress_callback(50)
            time.sleep(0.5)
            webbrowser.open(url_to_open)
            progress_callback(100)
            return True
        return False