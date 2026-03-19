import tkinter as tk
from tkinter import ttk, messagebox

class InkSiegeLauncher(tk.Tk):
    def __init__(self, data_list, install_fn):
        super().__init__()
        self.title("InkSiege Launcher v2.0")
        self.geometry("500x450")
        self.configure(bg="#0b0e14")
        
        self.data_list = data_list
        self.install_fn = install_fn
        self._init_ui()

    def _init_ui(self):
        # Header Neón
        header = tk.Frame(self, bg="#161b22", height=70)
        header.pack(fill="x")
        tk.Label(header, text="INKSIEGE SDK", fg="#58a6ff", bg="#161b22", 
                 font=("Segoe UI", 18, "bold")).pack(pady=15)

        # Main Area
        container = tk.Frame(self, bg="#0b0e14", padx=30)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="VERSIÓN DEL PROYECTO", fg="#8b949e", bg="#0b0e14", 
                 font=("Segoe UI", 9)).pack(pady=(20,5), anchor="w")

        self.v_var = tk.StringVar(value=self.data_list[0]['v'])
        self.menu = tk.OptionMenu(container, self.v_var, *[d['v'] for d in self.data_list], command=self._update_display)
        self.menu.config(bg="#21262d", fg="white", bd=0, highlightthickness=0)
        self.menu.pack(fill="x")

        # Info Box
        self.info_box = tk.Label(container, text=self.data_list[0]['info'], bg="#161b22", 
                                 fg="#c9d1d9", wraplength=400, pady=20, font=("Segoe UI", 10))
        self.info_box.pack(fill="x", pady=20)

        # Progress
        self.pb = ttk.Progressbar(container, mode='determinate', length=400)
        self.pb.pack(fill="x", pady=10)
        
        self.status = tk.Label(container, text="Esperando selección...", fg="#8b949e", bg="#0b0e14")
        self.status.pack()

        # Botón
        self.btn = tk.Button(container, text="DESCARGAR E INSTALAR", bg="#238636", fg="white", 
                             font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", 
                             command=self._start_task)
        self.btn.pack(fill="x", side="bottom", pady=20, ipady=10)

    def _update_display(self, val):
        item = next(i for i in self.data_list if i['v'] == val)
        self.info_box.config(text=item['info'])

    def _start_task(self):
        val = self.v_var.get()
        item = next(i for i in self.data_list if i['v'] == val)
        self.btn.config(state="disabled")
        self.install_fn(item, self._update_pb)

    def _update_pb(self, val):
        self.pb['value'] = val
        self.status.config(text=f"Procesando... {val}%")
        self.update()
        if val == 100:
            self.btn.config(state="normal")
            messagebox.showinfo("InkSiege", "Se ha abierto el navegador para la descarga.")