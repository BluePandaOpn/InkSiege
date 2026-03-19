import customtkinter as ctk
from tkinter import messagebox
import threading

class InkSiegeLauncher(ctk.CTk):
    def __init__(self, data_list, action_fn):
        super().__init__()
        self.title("InkSiege SDK Pro v2.5")
        self.geometry("650x550")
        self.configure(fg_color="#0d1117") 
        
        self.data_list = data_list
        self.action_fn = action_fn
        self._init_ui()

    def _init_ui(self):
        # Título
        ctk.CTkLabel(self, text="INKSIEGE SYSTEM", font=("Segoe UI", 28, "bold"), text_color="#58a6ff").pack(pady=25)

        # Panel Central
        frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=15)
        frame.pack(fill="both", expand=True, padx=40, pady=10)

        # Selección de Versión
        ctk.CTkLabel(frame, text="VERSIONES DISPONIBLES", font=("Segoe UI", 11, "bold")).pack(pady=(20,5))
        self.v_var = ctk.StringVar(value=self.data_list[0]['v'])
        self.menu = ctk.CTkOptionMenu(frame, variable=self.v_var, 
                                      values=[d['v'] for d in self.data_list],
                                      command=self._update_display,
                                      fg_color="#21262d", button_color="#30363d")
        self.menu.pack(fill="x", padx=40, pady=10)

        # Notas de Versión
        self.info_box = ctk.CTkTextbox(frame, height=120, fg_color="#0d1117", border_width=1)
        self.info_box.pack(fill="x", padx=40, pady=10)
        self._update_display(self.v_var.get())

        # Barra de progreso decorativa
        self.pb = ctk.CTkProgressBar(frame, progress_color="#238636")
        self.pb.pack(fill="x", padx=40, pady=20)
        self.pb.set(0)

        # Botones de Acción
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=30)

        self.btn_inst = ctk.CTkButton(btn_frame, text="INSTALAR (.EXE)", fg_color="#238636", 
                                      hover_color="#2ea043", command=lambda: self._exec(False))
        self.btn_inst.pack(side="left", expand=True, padx=5, ipady=8)

        self.btn_upd = ctk.CTkButton(btn_frame, text="ACTUALIZAR (.ZIP)", fg_color="#1f6feb", 
                                     hover_color="#388bfd", command=lambda: self._exec(True))
        self.btn_upd.pack(side="right", expand=True, padx=5, ipady=8)

    def _update_display(self, val):
        item = next(i for i in self.data_list if i['v'] == val)
        self.info_box.configure(state="normal")
        self.info_box.delete("0.0", "end")
        self.info_box.insert("0.0", f"DESCRIPCIÓN: {item['info']}\n\nRUTA: {item['path_install']}")
        self.info_box.configure(state="disabled")

    def _exec(self, is_update):
        threading.Thread(target=self._run_logic, args=(is_update,), daemon=True).start()

    def _run_logic(self, is_update):
        self.pb.set(0.5)
        val = self.v_var.get()
        item = next(i for i in self.data_list if i['v'] == val)
        
        success, msg = self.action_fn(item, is_update)
        self.pb.set(1.0)
        
        if success:
            messagebox.showinfo("InkSiege", msg)
        else:
            messagebox.showerror("Error", msg)
        self.pb.set(0)