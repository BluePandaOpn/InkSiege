import tkinter as tk
from tkinter import messagebox, ttk
import threading

class SDKGui(tk.Tk):
    def __init__(self, version_list, on_install_callback):
        super().__init__()
        self.title("InkSiege Launcher Pro")
        self.geometry("500x450")
        self.configure(bg="#0a0a0a")
        self.version_list = version_list
        self.on_install = on_install_callback
        
        self._create_widgets()

    def _create_widgets(self):
        # Cabecera
        header = tk.Frame(self, bg="#111", height=80)
        header.pack(fill="x")
        tk.Label(header, text="INKSIEGE SDK", bg="#111", fg="#00f2ff", 
                 font=("Impact", 24)).pack(pady=10)

        # Contenedor
        main = tk.Frame(self, bg="#0a0a0a", padx=30)
        main.pack(fill="both", expand=True)

        tk.Label(main, text="SELECCIONAR VERSIÓN", bg="#0a0a0a", fg="#888", 
                 font=("Arial", 9, "bold")).pack(pady=(20, 5), anchor="w")

        # Selector
        self.selected_v = tk.StringVar(value=self.version_list[0]['v'])
        self.menu = tk.OptionMenu(main, self.selected_v, *[v['v'] for v in self.version_list], command=self.update_info)
        self.menu.config(bg="#1a1a1a", fg="white", highlightthickness=0, bd=0)
        self.menu.pack(fill="x")

        # Info Card
        self.info_card = tk.Label(main, text=self.version_list[0]['description'], bg="#1a1a1a", 
                                  fg="#ccc", wraplength=400, pady=20, font=("Arial", 10))
        self.info_card.pack(fill="x", pady=20)

        # Barra de Instalación
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=10)
        
        self.status_label = tk.Label(main, text="Listo para instalar", bg="#0a0a0a", fg="#00f2ff")
        self.status_label.pack()

        # Botón
        self.btn_action = tk.Button(main, text="INSTALAR / ACTUALIZAR", bg="#00f2ff", fg="black",
                                    font=("Arial", 10, "bold"), bd=0, pady=10, command=self.start_process)
        self.btn_action.pack(fill="x", side="bottom", pady=20)

    def update_info(self, val):
        for v in self.version_list:
            if v['v'] == val:
                self.info_card.config(text=v['description'])

    def start_process(self):
        v_data = next(v for v in self.version_list if v['v'] == self.selected_v.get())
        self.btn_action.config(state="disabled")
        
        # Ejecutar en hilo separado para no congelar la GUI
        thread = threading.Thread(target=self.on_install, args=(v_data, self.update_progress))
        thread.start()

    def update_progress(self, value):
        self.progress_var.set(value)
        self.status_label.config(text=f"Procesando: {int(value)}%")
        if value >= 100:
            self.status_label.config(text="¡Instalación Completada!")
            self.btn_action.config(state="normal")
            messagebox.showinfo("InkSiege", "El proyecto se ha actualizado con éxito.")