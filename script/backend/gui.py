import customtkinter as ctk
from tkinter import messagebox
import threading
import webbrowser
import time

class InkSiegeLauncher(ctk.CTk):
    def __init__(self, data_list, install_fn):
        super().__init__()
        self.title("InkSiege SDK Manager v2.5")
        self.geometry("600x520")
        self.configure(fg_color="#1a1a1a")
        
        self.data_list = data_list
        self.install_fn = install_fn
        self._init_ui()

    def _init_ui(self):
        ctk.CTkLabel(self, text="INKSIEGE SYSTEM", font=("Segoe UI", 24, "bold"), text_color="#58a6ff").pack(pady=20)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40)

        # Selección de Versión
        ctk.CTkLabel(container, text="Versión Detectada:", font=("Segoe UI", 12)).pack(anchor="w")
        self.v_var = ctk.StringVar(value=self.data_list[0]['v'])
        self.menu = ctk.CTkOptionMenu(container, variable=self.v_var, 
                                      values=[d['v'] for d in self.data_list],
                                      command=self._update_display,
                                      fg_color="#21262d", button_color="#30363d")
        self.menu.pack(fill="x", pady=(5, 15))

        # Cuadro de Notas
        self.info_box = ctk.CTkTextbox(container, height=120, corner_radius=10, border_width=1)
        self.info_box.pack(fill="x", pady=10)
        self.info_box.insert("0.0", self.data_list[0]['info'])
        self.info_box.configure(state="disabled")

        # Progreso
        self.pb = ctk.CTkProgressBar(container, progress_color="#238636")
        self.pb.pack(fill="x", pady=(20, 5))
        self.pb.set(0)

        self.status = ctk.CTkLabel(container, text="Esperando instrucción...", text_color="gray")
        self.status.pack()

        # Botón con estilo profesional
        self.btn = ctk.CTkButton(self, text="DESCARGAR E INSTALAR", 
                                 fg_color="#238636", hover_color="#2ea043",
                                 height=50, font=("Segoe UI", 14, "bold"),
                                 command=self._start_task)
        self.btn.pack(pady=30, padx=40, fill="x")

    def _update_display(self, val):
        item = next(i for i in self.data_list if i['v'] == val)
        self.info_box.configure(state="normal")
        self.info_box.delete("0.0", "end")
        self.info_box.insert("0.0", item['info'])
        self.info_box.configure(state="disabled")

    def _start_task(self):
        self.btn.configure(state="disabled")
        # El secreto para que no se congele es usar un Hilo (Thread)
        threading.Thread(target=self._proc_logic, daemon=True).start()

    def _proc_logic(self):
        val = self.v_var.get()
        item = next(i for i in self.data_list if i['v'] == val)
        
        # Simulación de preparación
        for p in [0.2, 0.5, 0.8]:
            self.pb.set(p)
            self.status.configure(text=f"Preparando manifiestos... {int(p*100)}%")
            time.sleep(0.3)
            
        success = self.install_fn(item, lambda x: None) # Usamos el updater original
        
        if success:
            self.pb.set(1.0)
            self.status.configure(text="Enlace abierto con éxito", text_color="#238636")
            messagebox.showinfo("InkSiege", "Se ha abierto la carpeta de Google Drive en su navegador.")
        else:
            self.status.configure(text="Error: URL no encontrada", text_color="#f85149")
            messagebox.showerror("Error", "No existe una URL válida para esta versión en SDL.install.")
            
        self.btn.configure(state="normal")