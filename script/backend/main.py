import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re
import threading
import webbrowser
import os
import time

# --- CONFIGURACIÓN GLOBAL ---
URL_SDK = "https://raw.githubusercontent.com/BluePandaOpn/InkSiege/refs/heads/main/script/version/SDK.version"
URL_SDL = "https://raw.githubusercontent.com/BluePandaOpn/InkSiege/refs/heads/main/script/version/SDL.install"

class SDKInterpreter:
    """Procesa los archivos de configuración remotos."""
    def __init__(self, sdk_content, sdl_content):
        self.sdk_content = sdk_content
        self.sdl_content = sdl_content

    def get_combined_data(self):
        # Extraer bloques: [SDK.Version] hasta [SDK]
        sdk_sections = re.findall(r"\[SDK\.Version\]\s*(V.*?)\n(.*?)\s*\[SDK\]", self.sdk_content, re.DOTALL)
        
        combined_list = []
        for version, body in sdk_sections:
            v_num = version.strip()
            v_clean = v_num.replace('V', '').strip()
            
            # Extraer Metadatos
            info = re.search(r"\[SDK\.Info\]\s*\"(.*?)\"", body)
            r_inst = re.search(r"\[SDK\.rute\.install\]\s*\"(.*?)\"", body)
            r_upd = re.search(r"\[SDK\.rute\.update\]\s*\"(.*?)\"", body)

            # Buscar URLs en el archivo SDL basado en la versión limpia (0.1, 0.1.1, etc)
            # Escapamos los puntos para la expresión regular
            v_esc = re.escape(v_clean)
            inst_pat = rf"\[SDL\.\({v_esc}\)\.install\.url\.general\]\s*\"(.*?)\""
            upd_pat = rf"\[SDL\.\({v_esc}\)\.update\.url\.general\]\s*\"(.*?)\""
            
            inst_url = re.search(inst_pat, self.sdl_content)
            upd_url = re.search(upd_pat, self.sdl_content)

            combined_list.append({
                "v": v_num,
                "info": info.group(1) if info else "Sin descripción.",
                "path_install": r_inst.group(1) if r_inst else "C:/InkSiege/Game",
                "path_update": r_upd.group(1) if r_upd else "C:/InkSiege/Patch",
                "url_install": inst_url.group(1) if inst_url and inst_url.group(1) else None,
                "url_update": upd_url.group(1) if upd_url and upd_url.group(1) else None
            })
            
        return combined_list

class InkSiegeApp(tk.Tk):
    def __init__(self, data_list):
        super().__init__()
        self.title("InkSiege SDK Professional Manager")
        self.geometry("600x550")
        self.configure(bg="#0d1117")
        self.data_list = data_list
        
        # Estilo de la Interfaz
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", thickness=10, troughcolor='#161b22', background='#238636')
        
        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#161b22", height=80)
        header.pack(fill="x")
        tk.Label(header, text="INKSIEGE SYSTEM", fg="#58a6ff", bg="#161b22", 
                 font=("Segoe UI", 20, "bold")).pack(pady=20)

        # Contenedor Principal
        container = tk.Frame(self, bg="#0d1117", padx=40)
        container.pack(fill="both", expand=True)

        # Selección de Versión
        tk.Label(container, text="VERSIÓN DISPONIBLE", fg="#8b949e", bg="#0d1117", 
                 font=("Segoe UI", 9, "bold")).pack(pady=(20, 5), anchor="w")
        
        self.v_var = tk.StringVar(value=self.data_list[0]['v'] if self.data_list else "N/A")
        self.v_menu = ttk.Combobox(container, textvariable=self.v_var, 
                                   values=[d['v'] for d in self.data_list], state="readonly")
        self.v_menu.pack(fill="x", pady=5)
        self.v_menu.bind("<<ComboboxSelected>>", self._on_version_change)

        # Información
        tk.Label(container, text="NOTAS DE LA VERSIÓN", fg="#8b949e", bg="#0d1117", 
                 font=("Segoe UI", 9, "bold")).pack(pady=(15, 5), anchor="w")
        
        self.info_box = tk.Text(container, height=6, bg="#161b22", fg="#c9d1d9", 
                                font=("Segoe UI", 10), bd=0, padx=10, pady=10)
        self.info_box.pack(fill="x")
        
        # Barra de progreso
        self.pb = ttk.Progressbar(container, orient="horizontal", mode="determinate")
        self.pb.pack(fill="x", pady=(25, 5))
        
        self.status_label = tk.Label(container, text="Listo para procesar", fg="#8b949e", bg="#0d1117")
        self.status_label.pack()

        # Botones
        btn_frame = tk.Frame(container, bg="#0d1117")
        btn_frame.pack(fill="x", pady=30)

        self.btn_install = tk.Button(btn_frame, text="INSTALACIÓN COMPLETA", bg="#238636", fg="white",
                                     font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                                     command=lambda: self._start_process(is_update=False))
        self.btn_install.pack(side="left", expand=True, fill="x", padx=(0, 10), ipady=10)

        self.btn_update = tk.Button(btn_frame, text="SOLO ACTUALIZAR", bg="#1f6feb", fg="white",
                                    font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2",
                                    command=lambda: self._start_process(is_update=True))
        self.btn_update.pack(side="right", expand=True, fill="x", padx=(10, 0), ipady=10)

        self._refresh_data()

    def _on_version_change(self, event):
        self._refresh_data()

    def _refresh_data(self):
        version_name = self.v_var.get()
        item = next((i for i in self.data_list if i['v'] == version_name), None)
        if item:
            self.info_box.config(state="normal")
            self.info_box.delete("1.0", "end")
            content = f"Info: {item['info']}\n\nRuta: {item['path_install']}"
            self.info_box.insert("1.0", content)
            self.info_box.config(state="disabled")

    def _start_process(self, is_update):
        # Bloquear botones para evitar múltiples clics
        self.btn_install.config(state="disabled")
        self.btn_update.config(state="disabled")
        
        # Ejecutar en hilo separado para que no se congele la ventana
        threading.Thread(target=self._logic_thread, args=(is_update,), daemon=True).start()

    def _logic_thread(self, is_update):
        version_name = self.v_var.get()
        item = next((i for i in self.data_list if i['v'] == version_name), None)
        
        if not item:
            self._update_ui("Error: Versión no encontrada", 0, "red")
            return

        url = item['url_update'] if is_update else item['url_install']
        path = item['path_update'] if is_update else item['path_install']

        if not url:
            self._update_ui("Error: URL no definida en SDL.install", 0, "#f85149")
            messagebox.showerror("Error de Configuración", f"No hay un enlace de Google Drive para la versión {version_name}")
            self.btn_install.config(state="normal")
            self.btn_update.config(state="normal")
            return

        # Simular preparación
        self._update_ui("Preparando directorios...", 30)
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
        except: pass
        
        time.sleep(0.8)
        self._update_ui("Abriendo Google Drive...", 70)
        webbrowser.open(url)
        time.sleep(0.5)
        
        self._update_ui("Proceso iniciado con éxito", 100, "#3fb950")
        messagebox.showinfo("InkSiege", f"Se ha abierto el enlace de {'Actualización' if is_update else 'Instalación'}.\n\nDestino: {path}")
        
        # Rehabilitar botones
        self.btn_install.config(state="normal")
        self.btn_update.config(state="normal")

    def _update_ui(self, status, progress, color="#8b949e"):
        self.status_label.config(text=status, fg=color)
        self.pb['value'] = progress
        self.update_idletasks()

def boot():
    """Iniciador del programa con manejo de errores de red."""
    print("Iniciando InkSiege Professional Launcher...")
    try:
        # Peticiones de red
        sdk_response = requests.get(URL_SDK, timeout=10).text
        sdl_response = requests.get(URL_SDL, timeout=10).text
        
        interpreter = SDKInterpreter(sdk_response, sdl_response)
        data = interpreter.get_combined_data()
        
        if not data:
            raise ValueError("No se encontraron versiones válidas en los archivos del servidor.")

        app = InkSiegeApp(data)
        app.mainloop()
        
    except Exception as e:
        # Fallback si no hay internet o GitHub falla
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error Crítico", f"No se pudo sincronizar con el servidor:\n{e}")
        root.destroy()

if __name__ == "__main__":
    boot()