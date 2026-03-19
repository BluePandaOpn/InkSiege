import requests

class AppUpdater:
    def __init__(self, github_url):
        self.url = github_url

    def download_manifest(self):
        """Descarga el archivo de texto desde GitHub."""
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status() # Lanza error si la descarga falla
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] No se pudo conectar a GitHub: {e}")
            return None

    def compare_versions(self, local_v, remote_v):
        """
        Compara versiones. 
        Retorna True si la remota es más nueva.
        """
        # Eliminamos la 'V' para comparar números
        l = local_v.replace('V', '').split('.')
        r = remote_v.replace('V', '').split('.')
        return r > l