import re

class SDKInterpreter:
    def __init__(self, sdk_content, sdl_content):
        self.sdk_content = sdk_content
        self.sdl_content = sdl_content

    def get_combined_data(self):
        # 1. Extraer Info de SDK.version
        sdk_pattern = r"\[SDK\.Version\]\s*(V[\d\.]+).*?\n\[SDK\.Info\]\s*\"(.*?)\""
        sdk_matches = re.findall(sdk_pattern, self.sdk_content, re.MULTILINE)

        # 2. Extraer URLs de SDL.install
        # Buscamos patrones como [SDL.(0.1.3).install.url.general]
        combined_list = []
        for v_raw, info in sdk_matches:
            # Limpiar 'V' para buscar en SDL (ej: V0.1.3 -> 0.1.3)
            v_clean = v_raw.replace('V', '')
            
            # Buscar Install URL
            inst_pat = rf"\[SDL\.\({v_clean}\)\.install\.url\.general\]\s*\"(.*?)\""
            upd_pat = rf"\[SDL\.\({v_clean}\)\.update\.url\.general\]\s*\"(.*?)\""
            
            install_url = re.search(inst_pat, self.sdl_content)
            update_url = re.search(upd_pat, self.sdl_content)

            combined_list.append({
                "v": v_raw,
                "info": info,
                "install_url": install_url.group(1) if install_url else "",
                "update_url": update_url.group(1) if update_url else ""
            })
            
        return combined_list[::-1] # Más reciente primero