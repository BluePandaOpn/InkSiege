import sys
import os
import subprocess
import threading
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFileDialog, QTextEdit, QCheckBox,
    QGroupBox, QRadioButton, QFrame, QScrollArea, QToolTip
)
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtGui import QFont, QIcon, QColor

class LogEmitter(QObject):
    log = pyqtSignal(str)
    done = pyqtSignal(bool)
    version_updated = pyqtSignal(str)

class LegendsCompiler(QWidget):
    def __init__(self):
        super().__init__()
        self.version_file = "version_control.json"
        self.emitter = LogEmitter()
        self.emitter.log.connect(self.log)
        self.emitter.done.connect(self.on_build_done)
        self.emitter.version_updated.connect(self.update_version_display)
        
        self.current_version = self.load_version()
        self.initUI()
        self.set_project_defaults()

    def load_version(self):
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"major": 0, "minor": 1, "patch": 0, "build": 0}

    def save_version(self, v):
        with open(self.version_file, "w") as f:
            json.dump(v, f, indent=4)

    def initUI(self):
        self.setWindowTitle("InkSiege - Ultra Compiler & Versioning")
        self.setMinimumWidth(850)
        self.setMinimumHeight(700)
        
        # Estilo Moderno Oscuro
        self.setStyleSheet("""
            QWidget { background-color: #1a1a1b; color: #d7dadc; font-family: 'Segoe UI', Arial; }
            QGroupBox { border: 2px solid #343536; border-radius: 8px; margin-top: 20px; padding-top: 15px; font-weight: bold; color: #4b6eaf; }
            QLineEdit { background-color: #272729; border: 1px solid #343536; padding: 8px; border-radius: 5px; color: white; }
            QPushButton { background-color: #0079d3; border: none; padding: 10px; border-radius: 5px; font-weight: bold; color: white; }
            QPushButton:hover { background-color: #1484d6; }
            QPushButton#buildBtn { background-color: #d93a00; font-size: 14px; }
            QPushButton#buildBtn:hover { background-color: #ff4500; }
            QCheckBox { spacing: 8px; }
            QTextEdit { background-color: #030303; border-radius: 5px; border: 1px solid #343536; }
        """)

        main_layout = QHBoxLayout(self)

        # Panel Izquierdo: Configuración
        left_panel = QVBoxLayout()
        
        # --- INFO DE VERSION ---
        ver_group = QGroupBox("Estado de la Versión Actual")
        ver_layout = QVBoxLayout()
        self.lbl_full_ver = QLabel(self.get_version_str())
        self.lbl_full_ver.setStyleSheet("font-size: 24px; color: #00ff7f; font-weight: bold;")
        self.lbl_full_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver_layout.addWidget(self.lbl_full_ver)
        ver_group.setLayout(ver_layout)
        left_panel.addWidget(ver_group)

        # --- CAMBIOS EN ESTA COMPILACIÓN ---
        changes_group = QGroupBox("¿Qué hay de nuevo en esta build?")
        changes_layout = QVBoxLayout()
        
        self.chk_major = QCheckBox("Gran Cambio / Rediseño (Aumenta Major)")
        self.chk_feat = QCheckBox("Nueva Funcionalidad / Item / Enemigo (Aumenta Minor)")
        self.chk_bug = QCheckBox("Corrección de Bugs / Parche (Aumenta Patch)")
        self.chk_build_only = QCheckBox("Solo Re-compilar (Aumenta Build)")
        self.chk_build_only.setChecked(True)

        changes_layout.addWidget(self.chk_major)
        changes_layout.addWidget(self.chk_feat)
        changes_layout.addWidget(self.chk_bug)
        changes_layout.addWidget(self.chk_build_only)
        changes_group.setLayout(changes_layout)
        left_panel.addWidget(changes_group)

        # --- ARCHIVOS ---
        file_group = QGroupBox("Rutas del Proyecto")
        file_layout = QVBoxLayout()
        self.input_main = self.create_input(file_layout, "Script Principal:", "main.py")
        self.input_icon = self.create_input(file_layout, "Icono (.ico):", "assets/icon.ico")
        self.input_assets = self.create_input(file_layout, "Carpeta Assets:", "assets")
        file_group.setLayout(file_layout)
        left_panel.addWidget(file_group)

        # --- OPCIONES ---
        opt_group = QGroupBox("Opciones de Empaquetado")
        opt_layout = QVBoxLayout()
        self.radio_onefile = QRadioButton("Portable (Un solo .exe)")
        self.radio_onedir = QRadioButton("Instalable (Carpeta con dependencias)")
        self.radio_onefile.setChecked(True)
        self.chk_console = QCheckBox("Mostrar Consola (Modo Debug)")
        opt_layout.addWidget(self.radio_onefile)
        opt_layout.addWidget(self.radio_onedir)
        opt_layout.addWidget(self.chk_console)
        opt_group.setLayout(opt_layout)
        left_panel.addWidget(opt_group)

        self.btn_build = QPushButton("GENERAR BUILD EJECUTABLE")
        self.btn_build.setObjectName("buildBtn")
        self.btn_build.setFixedHeight(60)
        self.btn_build.clicked.connect(self.start_build)
        left_panel.addWidget(self.btn_build)

        # Panel Derecho: Consola
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("LOG DE COMPILACIÓN:"))
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 10))
        right_panel.addWidget(self.console)

        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 3)

    def create_input(self, layout, label, placeholder):
        layout.addWidget(QLabel(label))
        row = QHBoxLayout()
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        btn = QPushButton("...")
        btn.setFixedWidth(40)
        btn.clicked.connect(lambda: self.browse_path(edit))
        row.addWidget(edit)
        row.addWidget(btn)
        layout.addLayout(row)
        return edit

    def browse_path(self, edit):
        path = QFileDialog.getOpenFileName(self, "Seleccionar")[0]
        if path: edit.setText(path)

    def get_version_str(self):
        v = self.current_version
        return f"V{v['major']}.{v['minor']}.{v['patch']}-build-{v['build']}"

    def update_version_display(self, text):
        self.lbl_full_ver.setText(text)

    def set_project_defaults(self):
        # Intentar auto-detectar main.py en la carpeta actual
        base = os.getcwd()
        main_path = os.path.join(base, "main.py")
        if os.path.exists(main_path):
            self.input_main.setText(main_path)
            
        assets_path = os.path.join(base, "assets")
        if os.path.exists(assets_path):
            self.input_assets.setText(assets_path)

    def calculate_new_version(self):
        v = self.current_version.copy()
        v["build"] += 1
        if self.chk_major.isChecked():
            v["major"] += 1
            v["minor"] = 0
            v["patch"] = 0
        elif self.chk_feat.isChecked():
            v["minor"] += 1
            v["patch"] = 0
        elif self.chk_bug.isChecked():
            v["patch"] += 1
        return v

    def log(self, text):
        self.console.append(text)
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    def start_build(self):
        if not self.input_main.text():
            self.log("❌ ERROR: Selecciona el archivo main.py")
            return
        
        self.btn_build.setEnabled(False)
        self.current_version = self.calculate_new_version()
        self.save_version(self.current_version)
        self.emitter.version_updated.emit(self.get_version_str())
        
        threading.Thread(target=self.run_process, daemon=True).start()

    def run_process(self):
        v_str = self.get_version_str()
        name = f"InkSiege_{v_str}"
        main_py = self.input_main.text()
        workdir = os.path.dirname(main_py)
        
        cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean"]
        
        if self.radio_onefile.isChecked(): cmd.append("--onefile")
        else: cmd.append("--onedir")
        
        if not self.chk_console.isChecked(): cmd.append("--windowed")
        
        # Icono
        if self.input_icon.text():
            cmd.extend(["--icon", self.input_icon.text()])
            
        # Assets automáticos
        assets = self.input_assets.text()
        if os.path.exists(assets):
            # Formato PyInstaller: "ruta_origen;ruta_destino_en_exe"
            cmd.extend(["--add-data", f"{assets}{os.pathsep}assets"])
        
        # También incluir bluepanda.py si está en el mismo sitio
        bp_path = os.path.join(workdir, "bluepanda.py")
        if os.path.exists(bp_path):
            cmd.extend(["--hidden-import", "bluepanda"])

        cmd.extend(["--name", name, main_py])

        try:
            self.emitter.log.emit(f"🚀 Iniciando Compilación de {v_str}...")
            process = subprocess.Popen(
                cmd, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            for line in process.stdout:
                self.emitter.log.emit(line.strip())

            process.wait()
            self.emitter.done.emit(process.returncode == 0)
        except Exception as e:
            self.emitter.log.emit(f"❌ ERROR CRÍTICO: {str(e)}")
            self.emitter.done.emit(False)

    def on_build_done(self, success):
        self.btn_build.setEnabled(True)
        if success:
            self.log(f"\n✅ ¡COMPILACIÓN EXITOSA!\nVersión: {self.get_version_str()}")
            dist = os.path.join(os.path.dirname(self.input_main.text()), "dist")
            if os.path.exists(dist): os.startfile(dist)
        else:
            self.log("\n❌ Falló el proceso. Revisa el log arriba.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Icono de app si existiera
    window = LegendsCompiler()
    window.show()
    sys.exit(app.exec())