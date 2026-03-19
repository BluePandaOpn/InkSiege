import tkinter as tk
from tkinter import messagebox, ttk

class InkSiegeLauncher(tk.Tk):
    def __init__(self, versions, install_callback):
        super().__init__()
        self.title("InkSiege SDK Manager")
        self.geometry("450x350")
        self.configure(bg="#1e1e1e") # Un tono oscuro más moderno
        
        self.versions = versions
        self.install_callback = install_callback

        # Título
        tk.Label(self, text="INSTALADOR DE VERSIONES SDK", fg="#00ff00", bg="#1e1e1e", 
                 font=("Courier", 12, "bold")).pack(pady=15)

        # Menú de Selección
        self.selected_v = tk.StringVar()
        v_names = [v['version'] for v in self.versions]
        self.selected_v.set(v_names[0])

        tk.Label(self, text="Selecciona Versión:", fg="white", bg="#1e1e1e").pack()
        self.menu = tk.OptionMenu(self, self.selected_v, *v_names, command=self.update_ui)
        self.menu.config(bg="#333", fg="white", width=15)
        self.menu.pack(pady=10)

        # Info de Versión
        self.info_var = tk.StringVar(value=f"Nota: {self.versions[0]['info']}")
        self.lbl_info = tk.Label(self, textvariable=self.info_var, fg="#aaa", bg="#1e1e1e", 
                                 wraplength=380, font=("Arial", 9, "italic"))
        self.lbl_info.pack(pady=10)

        # Botón de Acción
        self.btn = tk.Button(self, text="INSTALAR SELECCIÓN", bg="#0078d7", fg="white",
                             font=("Arial", 10, "bold"), command=self.run_install, padx=20)
        self.btn.pack(pady=20)

    def update_ui(self, selection):
        for v in self.versions:
            if v['version'] == selection:
                self.info_var.set(f"Nota: {v['info']}")

    def run_install(self):
        v = self.selected_v.get()
        if messagebox.askyesno("Confirmar", f"¿Instalar {v} de InkSiege?"):
            self.install_callback(v)
            messagebox.showinfo("Éxito", f"Versión {v} configurada correctamente.")