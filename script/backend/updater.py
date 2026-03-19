import webbrowser
import os

class SDKUpdater:
    @staticmethod
    def process_action(data, is_update=False):
        """
        Lógica para preparar carpetas y abrir el enlace de descarga.
        """
        url = data['url_update'] if is_update else data['url_install']
        path = data['path_update'] if is_update else data['path_install']

        if not url:
            return False, "Error: No se encontró una URL válida para esta versión."

        # Intentar crear el directorio de destino antes de descargar
        try:
            if path and not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
        except Exception as e:
            return False, f"No se pudo crear la ruta: {e}"

        # Abrir el navegador (Drive no permite descarga directa por script fácilmente)
        webbrowser.open(url)
        return True, f"Carpeta de destino preparada en: {path}"