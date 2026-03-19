import re

class SDKInterpreter:
    def __init__(self, sdk_content, sdl_content):
        self.sdk_content = sdk_content
        self.sdl_content = sdl_content

    def get_combined_data(self):
        # Extraer bloques completos: Versión hasta el tag [SDK]
        sdk_sections = re.findall(r"\[SDK\.Version\]\s*(V.*?)\n(.*?)\s*\[SDK\]", self.sdk_content, re.DOTALL)
        
        combined_list = []
        for version, body in sdk_sections:
            v_num = version.strip()
            # Limpiamos 'V' para buscar en SDL (ej: V0.1.3 -> 0.1.3)
            v_clean = v_num.replace('V', '').strip()
            
            # Extraer Info y Rutas del cuerpo del SDK
            info = re.search(r"\[SDK\.Info\]\s*\"(.*?)\"", body)
            r_inst = re.search(r"\[SDK\.rute\.install\]\s*\"(.*?)\"", body)
            r_upd = re.search(r"\[SDK\.rute\.update\]\s*\"(.*?)\"", body)

            # Buscar las URLs específicas en tu archivo SDL proporcionado
            inst_pat = rf"\[SDL\.\({re.escape(v_clean)}\)\.install\.url\.general\]\s*\"(.*?)\""
            upd_pat = rf"\[SDL\.\({re.escape(v_clean)}\)\.update\.url\.general\]\s*\"(.*?)\""
            
            inst_url = re.search(inst_pat, self.sdl_content)
            upd_url = re.search(upd_pat, self.sdl_content)

            combined_list.append({
                "v": v_num,
                "info": info.group(1) if info else "Sin descripción disponible.",
                "path_install": r_inst.group(1) if r_inst else "C:/InkSiege/Game",
                "path_update": r_upd.group(1) if r_upd else "C:/InkSiege/Game/Updates",
                "url_install": inst_url.group(1) if inst_url and inst_url.group(1) else None,
                "url_update": upd_url.group(1) if upd_url and upd_url.group(1) else None
            })
            
        return combined_list # Retorna la lista de versiones procesadas