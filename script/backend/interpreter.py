import re

class SDKInterpreter:
    def __init__(self, sdk_content, sdl_content):
        self.sdk_content = sdk_content
        self.sdl_content = sdl_content

    def get_combined_data(self):
        # Extrae Versión y Descripción del SDK.version
        sdk_pattern = r"\[SDK\.Version\]\s*(V[\d\.]+)\s*\[SDK\.Info\]\s*\"(.*?)\""
        sdk_matches = re.findall(sdk_pattern, self.sdk_content, re.DOTALL)

        combined_list = []
        for v_raw, info in sdk_matches:
            # Limpiar 'V' para buscar en el archivo SDL (ej: V0.1.3 -> 0.1.3)
            v_clean = v_raw.replace('V', '').strip()
            
            # Patrones flexibles para encontrar las URLs de Google Drive
            inst_pat = rf"\[SDL\.\({re.escape(v_clean)}\)\.install\.url\.general\]\s*\"(.*?)\""
            upd_pat = rf"\[SDL\.\({re.escape(v_clean)}\)\.update\.url\.general\]\s*\"(.*?)\""
            
            install_url = re.search(inst_pat, self.sdl_content)
            update_url = re.search(upd_pat, self.sdl_content)

            combined_list.append({
                "v": v_raw,
                "info": info.strip(),
                "install_url": install_url.group(1) if install_url and install_url.group(1) else None,
                "update_url": update_url.group(1) if update_url and update_url.group(1) else None
            })
            
        return combined_list #