import re

class SDKInterpreter:
    def __init__(self, raw_content):
        self.content = raw_content

    def get_versions(self):
        # Regex mejorada para capturar Version, Info, Install Path y Update Path
        pattern = (r"\[SDK\.Version\]\s*(V[\d\.]+).*?\n"
                   r"\[SDK\.Info\]\s*\"(.*?)\".*?\n"
                   r"\[SDK\.rute\.install\]\s*\"(.*?)\".*?\n"
                   r"\[SDK\.rute\.update\]\s*\"(.*?)\".*?\n"
                   r"\[SDK\]")
        
        matches = re.findall(pattern, self.content, re.MULTILINE | re.DOTALL)
        
        parsed_data = []
        for v, info, r_install, r_update in matches:
            parsed_data.append({
                "v": v.strip(),
                "description": info.strip(),
                "install_url": r_install.strip(),
                "update_url": r_update.strip()
            })
        return parsed_data[::-1]