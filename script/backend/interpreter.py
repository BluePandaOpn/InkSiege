import re

class SDKInterpreter:
    def __init__(self, content):
        self.content = content

    def get_all_versions(self):
        """Retorna una lista con todos los bloques de versiones encontrados."""
        # Buscamos el patrón: Version, Info y el cierre [SDK]
        pattern = r"\[SDK\.Version\]\s*(V[\d\.]+)\n\[SDK\.Info\]\s*\"(.*?)\"\n\[SDK\]"
        matches = re.findall(pattern, self.content, re.MULTILINE)
        
        versions_list = []
        for v, info in matches:
            versions_list.append({
                "version": v.strip(),
                "info": info.strip()
            })
        # Invertimos para que la más reciente aparezca arriba en la lista
        return versions_list[::-1]