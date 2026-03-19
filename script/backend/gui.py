import tkinter as tk
from tkinter import messagebox, ttk

class SDKLauncher(tk.Tk):
    def __init__(self, versions_data, callback_install):
        super().__init__()
        self.title("SDK Version Selector")
        self.geometry("450x300")
        self.versions_data = versions_data # Lista de dicts {'version', 'info'}
        self.callback_install = callback_install

        # --- Interfaz ---
        tk.Label(self, text="Seleccione la versión a instalar:", font=("Arial", 10, "bold")).pack(pady=10)

        # Variable para el menú desplegable
        self.selected_version = tk.StringVar()
        # Creamos una lista solo con los nombres de las versiones para el menú
        version_names = [v['version'] for v in self.versions_data]
        self.selected_version.set(version_names[0]) # Seleccionar la primera por defecto

        self.menu = tk.OptionMenu(self, self.selected_version, *version_names, command=self.update_info_label)
        self.menu.pack(pady=5)

        # Cuadro de información de la versión seleccionada
        self.info_text = tk.StringVar(value=f"Info: {self.versions_data[0]['info']}")
        self.label_info = tk.Label(self, textvariable=self.info_text, wraplength=350, fg="gray")
        self.label_info.pack(pady=10)

        self.btn_install = tk.Button(self, text="Instalar / Downgrade", command=self.run_install, bg="#3498db", fg="white", width=20)
        self.btn_install.pack(pady=20)

    def update_info_label(self, selection):
        """Actualiza el texto descriptivo cuando cambias la versión en el menú."""
        for v in self.versions_data:
            if v['version'] == selection:
                self.info_text.set(f"Info: {v['info']}")

    def run_install(self):
        v_to_install = self.selected_version.get()
        confirm = messagebox.askyesno("Confirmar", f"¿Desea instalar la versión {v_to_install}?")
        if confirm:
            self.callback_install(v_to_install)

    def show_msg(self, title, msg):
        messagebox.showinfo(title, msg)