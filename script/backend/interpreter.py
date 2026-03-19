import re

class SDKInterpreter:
    def __init__(self, content):
        self.content = content

    def get_all_versions(self):
        """Extrae todas las versiones del archivo de InkSiege."""
        # Regex mejorada para capturar exactamente tu formato
        pattern = r"\[SDK\.Version\]\s*(V[\d\.]+)\n\[SDK\.Info\]\s*\"(.*?)\"\n\[SDK\]"
        matches = re.findall(pattern, self.content, re.DOTALL)
        
        versions_list = []
        for v, info in matches:
            versions_list.append({
                "version": v.strip(),
                "info": info.strip()
            })
        # Las devolvemos en orden inverso (la más reciente primero)
        return versions_list[::-1]