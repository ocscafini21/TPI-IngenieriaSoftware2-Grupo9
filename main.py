import os
import yaml
import tkinter as tk
from tkinter import ttk
from datetime import datetime

DATA_FILE = "database.yaml"

def init_db():
    if not os.path.exists(DATA_FILE):
        data = {
            "turnos": [],
            "usuarios": [
                {"usuario": "admin", "pass": "1234", "rol": "Secretaria"},
                {"usuario": "amado", "pass": "medico2026", "rol": "Médico"}
            ],
            "obras_sociales": [
                "Particular (Sin Cobertura)", "OSDE", "Swiss Medical", "Galeno",
                "IOMA", "PAMI", "Medicus", "OMINT", "Luis Pasteur", "Sancor Salud", "Accord Salud"
            ],
            "bloqueos": [],
            "auditoria": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

def load_data():
    if not os.path.exists(DATA_FILE):
        init_db()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
        if "auditoria" not in data:
            data["auditoria"] = []
        return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

class ConsultorioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión - Consultorio Dr. Salvador Amado")
        self.root.geometry("1100x850")
        
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        init_db()
        self.usuario_actual = None
        self.rol_actual = None
        self.main_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.usuario_actual = None
        self.rol_actual = None
        self.clear_window()

        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.rowconfigure(4, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        tk.Label(main_frame, text="Clínica Médica - Dr. Salvador Amado", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=20)
        tk.Label(main_frame, text="Seleccione el módulo de acceso:", font=("Arial", 11, "italic")).grid(row=1, column=0, pady=5)

        tk.Button(main_frame, text="👤 Módulo Paciente / Autogestión de Turnos (Sin Login)", width=48, height=2, bg="#e1f5fe", command=self.patient_view).grid(row=2, column=0, pady=10)
        tk.Button(main_frame, text="👩‍💼 Panel Administrativo / Secretaria (Login)", width=48, height=2, bg="#e8f5e9", command=lambda: self.login_view("Secretaria")).grid(row=3, column=0, pady=10)
        tk.Button(main_frame, text="🩺 Panel Médico / Super Admin - Dr. Amado (Login)", width=48, height=2, bg="#fff3e0", command=lambda: self.login_view("Médico")).grid(row=4, column=0, pady=10)
        tk.Button(main_frame, text="❌ Salir del Sistema", width=25, command=self.root.quit).grid(row=5, column=0, pady=20)

    # --- LOGIN UNIFICADO ---
    def login_view(self, rol_requerido):
        self.clear_window()
        
        login_frame = tk.Frame(self.root)
        login_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        login_frame.rowconfigure(3, weight=1)
        login_frame.columnconfigure(0, weight=1)

        tk.Label(login_frame, text=f"Acceso Restringido - Rol: {rol_requerido}", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=20)

        form_sub = tk.Frame(login_frame)
        form_sub.grid(row=1, column=0, pady=5)

        tk.Label(form_sub, text="Usuario:").grid(row=0, column=0, sticky="w", pady=5)
        e_user = tk.Entry(form_sub, width=30)
        e_user.grid(row=0, column=1, pady=5)

        tk.Label(form_sub, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=5)
        e_pass = tk.Entry(form_sub, width=30, show="*")
        e_pass.grid(row=1, column=1, pady=5)

        lbl_status = tk.Label(login_frame, text="", font=("Arial", 9, "bold"))
        lbl_status.grid(row=2, column=0, pady=5)

        def validar_ingreso():
            data = load_data()
            usuario_ingresado = e_user.get().strip()
            pass_ingresada = e_pass.get().strip()

            for u in data["usuarios"]:
                if u["usuario"] == usuario_ingresado and u["pass"] == pass_ingresada and u["rol"] == rol_requerido:
                    self.usuario_actual = usuario_ingresado
                    self.rol_actual = rol_requerido
                    if rol_requerido == "Secretaria":
                        self.secretary_view()
                    else:
                        self.doctor_view()
                    return
            
            lbl_status.config(text="Error: Usuario, contraseña o rol incorrectos.", fg="red")

        btn_sub = tk.Frame(login_frame)
        btn_sub.grid(row=3, column=0, pady=10)
        tk.Button(btn_sub, text="Ingresar al Sistema", bg="green", fg="white", width=25, command=validar_ingreso).pack(pady=5)
        tk.Button(btn_sub, text="Volver al Menú Principal", width=25, command=self.main_menu).pack(pady=5)

    # --- SELECTOR DE HORARIO INTEGRADO Y VALIDACIÓN TEMPORAL ---
    def crear_selector_horario_integrado(self, parent_frame, callback_asignar, row_idx):
        frame_selector = tk.LabelFrame(parent_frame, text=" 📅 Selector de Fecha y Horario ", padx=10, pady=10)
        frame_selector.grid(row=row_idx, column=0, sticky="nsew", padx=10, pady=5)
        frame_selector.columnconfigure(1, weight=1)

        tk.Label(frame_selector, text="Fecha (DD/MM/AAAA):", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", pady=2)
        e_fecha = tk.Entry(frame_selector, width=15)
        e_fecha.grid(row=0, column=1, sticky="w", pady=2)
        e_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))

        tk.Label(frame_selector, text="Horarios Disponibles (Lun-Vie 8 a 16hs):", font=("Arial", 9, "italic")).grid(row=1, column=0, columnspan=2, sticky="w", pady=5)

        horarios_base = []
        for h in range(8, 16):
            horarios_base.append(f"{h:02d}:00")
            if h < 16:
                horarios_base.append(f"{h:02d}:30")

        listbox_horas = tk.Listbox(frame_selector, width=35, height=5)
        listbox_horas.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=3)

        for hora in horarios_base:
            listbox_horas.insert(tk.END, hora)

        lbl_aviso_sel = tk.Label(frame_selector, text="", font=("Arial", 9, "bold"))
        lbl_aviso_sel.grid(row=4, column=0, columnspan=2, pady=3)

        def procesar_seleccion():
            fecha_str = e_fecha.get()
            try:
                dt_fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
                if dt_fecha.weekday() > 4:
                    lbl_aviso_sel.config(text="Error: El consultorio solo atiende de Lunes a Viernes.", fg="red")
                    return
            except ValueError:
                lbl_aviso_sel.config(text="Error: Formato de fecha inválido (Use DD/MM/AAAA).", fg="red")
                return

            try:
                selected_idx = listbox_horas.curselection()[0]
                hora_str = listbox_horas.get(selected_idx)
            except IndexError:
                lbl_aviso_sel.config(text="Aviso: Seleccione un horario de la lista.", fg="red")
                return

            dt_completo = datetime.strptime(f"{fecha_str} {hora_str}", "%d/%m/%Y %H:%M")
            if dt_completo < datetime.now():
                lbl_aviso_sel.config(text="Error: No se pueden seleccionar fechas u horas pasadas.", fg="red")
                return

            fecha_hora_completa = f"{fecha_str} - {hora_str} hs"

            data = load_data()
            for t in data["turnos"]:
                if t["fecha"] == fecha_hora_completa:
                    lbl_aviso_sel.config(text="Conflicto: Este horario ya se encuentra ocupado.", fg="red")
                    return

            callback_asignar(fecha_hora_completa)
            lbl_aviso_sel.config(text=f"Horario seleccionado: {fecha_hora_completa}", fg="green")

        tk.Button(frame_selector, text="Confirmar este Horario", bg="#0288d1", fg="white", command=procesar_seleccion).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

    # --- WIDGET AUXILIAR DE TEXTO SCROLLABLE (VERTICAL Y HORIZONTAL) ---
    def crear_caja_texto_desplazable(self, parent_frame, altura=8):
        container = tk.Frame(parent_frame)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        txt_widget = tk.Text(container, wrap="none", font=("Consolas", 10), bg="#f9f9f9", fg="#333333", height=altura)
        txt_widget.grid(row=0, column=0, sticky="nsew")

        scroll_y = tk.Scrollbar(container, orient="vertical", command=txt_widget.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")

        scroll_x = tk.Scrollbar(container, orient="horizontal", command=txt_widget.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")

        txt_widget.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        return txt_widget

    # --- MÓDULO PACIENTE (AUTOGESTIÓN DIRECTA SIN LOGIN) ---
    def patient_view(self):
        self.clear_window()
        
        pat_frame = tk.Frame(self.root)
        pat_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        pat_frame.columnconfigure(0, weight=1)
        pat_frame.rowconfigure(2, weight=1)

        tk.Label(pat_frame, text="Portal de Autogestión - Turnos (Paciente)", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=10)

        form_frame = tk.Frame(pat_frame)
        form_frame.grid(row=1, column=0, sticky="ew", pady=5)
        form_frame.columnconfigure(1, weight=1)

        tk.Label(form_frame, text="Nombre y Apellido:").grid(row=0, column=0, sticky="w", pady=2)
        e_nombre = tk.Entry(form_frame, width=40)
        e_nombre.grid(row=0, column=1, sticky="ew", pady=2)

        tk.Label(form_frame, text="DNI:").grid(row=1, column=0, sticky="w", pady=2)
        e_dni = tk.Entry(form_frame, width=40)
        e_dni.grid(row=1, column=1, sticky="ew", pady=2)

        tk.Label(form_frame, text="Teléfono:").grid(row=2, column=0, sticky="w", pady=2)
        e_contacto = tk.Entry(form_frame, width=40)
        e_contacto.grid(row=2, column=1, sticky="ew", pady=2)

        tk.Label(form_frame, text="Obra Social:").grid(row=3, column=0, sticky="w", pady=2)
        data_init = load_data()
        combo_os = ttk.Combobox(form_frame, values=data_init["obras_sociales"], width=38, state="readonly")
        combo_os.grid(row=3, column=1, sticky="ew", pady=2)
        combo_os.current(0)

        tk.Label(form_frame, text="Nro Afiliado:").grid(row=4, column=0, sticky="w", pady=2)
        e_afiliado = tk.Entry(form_frame, width=40)
        e_afiliado.grid(row=4, column=1, sticky="ew", pady=2)
        e_afiliado.insert(0, "Particular / Sin credencial")

        lbl_turno = tk.Label(pat_frame, text="Turno seleccionado: [Ninguno]", font=("Arial", 10, "bold"), fg="#1565c0")
        lbl_turno.grid(row=2, column=0, pady=5)

        turno_seleccionado = {"val": ""}

        def asignar_horario_paciente(fh):
            turno_seleccionado["val"] = fh
            lbl_turno.config(text=f"Turno seleccionado: {fh}")

        self.crear_selector_horario_integrado(pat_frame, asignar_horario_paciente, row_idx=3)

        lbl_feedback = tk.Label(pat_frame, text="", font=("Arial", 9, "bold"))
        lbl_feedback.grid(row=4, column=0, pady=2)

        def reservar():
            if not e_nombre.get() or not e_dni.get() or not e_contacto.get() or not turno_seleccionado["val"]:
                lbl_feedback.config(text="Error: Complete todos los datos y seleccione un horario.", fg="red")
                return
            
            data = load_data()
            ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            nuevo_turno = {
                "paciente": e_nombre.get(),
                "dni": e_dni.get(),
                "contacto": e_contacto.get(),
                "fecha": turno_seleccionado["val"],
                "obra_social": combo_os.get(),
                "afiliado": e_afiliado.get(),
                "estado": "Pendiente",
                "requiere_nuevo_turno": False,
                "creado_por": f"Autogestión Paciente ({e_nombre.get()})",
                "modificado_por": f"Autogestión Paciente ({e_nombre.get()})",
                "fecha_modificacion": ahora_str
            }
            data["turnos"].append(nuevo_turno)
            data["auditoria"].append(f"[{ahora_str}] Turno creado por Autogestión Paciente DNI {e_dni.get()}")
            save_data(data)
            lbl_feedback.config(text="¡Turno reservado correctamente!", fg="green")
            self.root.after(1500, self.main_menu)

        btn_box = tk.Frame(pat_frame)
        btn_box.grid(row=5, column=0, pady=10)
        tk.Button(btn_box, text="Confirmar Reserva de Turno", bg="green", fg="white", font=("Arial", 10, "bold"), command=reservar).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_box, text="Volver al Menú Principal", command=self.main_menu).pack(side=tk.LEFT, padx=5)

    # --- CAMBIO DE CONTRASEÑA PROPIO ---
    def abrir_cambio_password(self):
        win_pass = tk.Toplevel(self.root)
        win_pass.title(f"Cambiar Contraseña - {self.usuario_actual}")
        win_pass.geometry("380x260")

        tk.Label(win_pass, text="Contraseña Actual:").pack(pady=5)
        e_actual = tk.Entry(win_pass, show="*", width=30)
        e_actual.pack(pady=2)

        tk.Label(win_pass, text="Nueva Contraseña:").pack(pady=5)
        e_nueva = tk.Entry(win_pass, show="*", width=30)
        e_nueva.pack(pady=2)

        lbl_msg = tk.Label(win_pass, text="", font=("Arial", 9, "bold"))
        lbl_msg.pack(pady=3)

        def guardar_cambio():
            data = load_data()
            pass_act = e_actual.get().strip()
            pass_nue = e_nueva.get().strip()

            if not pass_act or not pass_nue:
                lbl_msg.config(text="Complete ambos campos.", fg="red")
                return

            for u in data["usuarios"]:
                if u["usuario"] == self.usuario_actual:
                    if u["pass"] == pass_act:
                        u["pass"] = pass_nue
                        ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                        data["auditoria"].append(f"[{ahora_str}] Contraseña cambiada por usuario '{self.usuario_actual}'")
                        save_data(data)
                        lbl_msg.config(text="Contraseña actualizada con éxito.", fg="green")
                        win_pass.after(1200, win_pass.destroy)
                        return
                    else:
                        lbl_msg.config(text="Contraseña actual incorrecta.", fg="red")
                        return

        tk.Button(win_pass, text="Guardar Nueva Contraseña", bg="green", fg="white", command=guardar_cambio).pack(pady=10)

    # --- MÓDULO SECRETARIA (MODULAR CON PESTAÑAS) ---
    def secretary_view(self):
        self.clear_window()
        
        sec_frame = tk.Frame(self.root)
        sec_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        sec_frame.columnconfigure(0, weight=1)
        sec_frame.rowconfigure(1, weight=1)

        top_bar = tk.Frame(sec_frame)
        top_bar.grid(row=0, column=0, sticky="ew", pady=5)
        tk.Label(top_bar, text=f"Panel Administrativo - Secretaria ({self.usuario_actual})", font=("Arial", 13, "bold")).pack(side=tk.LEFT)
        tk.Button(top_bar, text="🔑 Cambiar mi Contraseña", bg="#0288d1", fg="white", command=self.abrir_cambio_password).pack(side=tk.RIGHT)

        notebook = ttk.Notebook(sec_frame)
        notebook.grid(row=1, column=0, sticky="nsew", pady=5)

        tab_crear = tk.Frame(notebook)
        tab_modificar = tk.Frame(notebook)
        tab_info = tk.Frame(notebook)

        notebook.add(tab_crear, text=" ➕ Crear Turno ")
        notebook.add(tab_modificar, text=" ✏️ Modificar / Cancelar Turno ")
        notebook.add(tab_info, text=" 📋 Información y Detalles de Turnos ")

        # ==================== PESTAÑA 1: CREAR TURNO ====================
        tab_crear.columnconfigure(0, weight=1)
        tk.Label(tab_crear, text="Registrar Nuevo Turno desde Secretaría", font=("Arial", 11, "bold")).grid(row=0, column=0, pady=10)

        form_c = tk.Frame(tab_crear)
        form_c.grid(row=1, column=0, sticky="ew", padx=10)
        form_c.columnconfigure(1, weight=1)

        tk.Label(form_c, text="Nombre y Apellido Paciente:").grid(row=0, column=0, sticky="w", pady=2)
        ec_nombre = tk.Entry(form_c, width=35)
        ec_nombre.grid(row=0, column=1, sticky="ew", pady=2)

        tk.Label(form_c, text="DNI:").grid(row=1, column=0, sticky="w", pady=2)
        ec_dni = tk.Entry(form_c, width=35)
        ec_dni.grid(row=1, column=1, sticky="ew", pady=2)

        tk.Label(form_c, text="Teléfono:").grid(row=2, column=0, sticky="w", pady=2)
        ec_contacto = tk.Entry(form_c, width=35)
        ec_contacto.grid(row=2, column=1, sticky="ew", pady=2)

        tk.Label(form_c, text="Obra Social:").grid(row=3, column=0, sticky="w", pady=2)
        data_init = load_data()
        cc_os = ttk.Combobox(form_c, values=data_init["obras_sociales"], width=33, state="readonly")
        cc_os.grid(row=3, column=1, sticky="ew", pady=2)
        cc_os.current(0)

        tk.Label(form_c, text="Nro Afiliado:").grid(row=4, column=0, sticky="w", pady=2)
        ec_afiliado = tk.Entry(form_c, width=35)
        ec_afiliado.grid(row=4, column=1, sticky="ew", pady=2)
        ec_afiliado.insert(0, "Particular / Sin credencial")

        lbl_turno_c = tk.Label(tab_crear, text="Turno seleccionado: [Ninguno]", font=("Arial", 10, "bold"), fg="#1565c0")
        lbl_turno_c.grid(row=2, column=0, pady=5)

        sel_c = {"val": ""}
        def asignar_c(fh):
            sel_c["val"] = fh
            lbl_turno_c.config(text=f"Turno seleccionado: {fh}")

        self.crear_selector_horario_integrado(tab_crear, asignar_c, row_idx=3)
        lbl_fb_c = tk.Label(tab_crear, text="", font=("Arial", 9, "bold"))
        lbl_fb_c.grid(row=4, column=0, pady=2)

        def guardar_turno_sec():
            if not ec_nombre.get() or not ec_dni.get() or not ec_contacto.get() or not sel_c["val"]:
                lbl_fb_c.config(text="Error: Complete los campos y seleccione un horario.", fg="red")
                return
            d = load_data()
            ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            t_nuevo = {
                "paciente": ec_nombre.get(),
                "dni": ec_dni.get(),
                "contacto": ec_contacto.get(),
                "fecha": sel_c["val"],
                "obra_social": cc_os.get(),
                "afiliado": ec_afiliado.get(),
                "estado": "Pendiente",
                "requiere_nuevo_turno": False,
                "creado_por": f"Secretaria ({self.usuario_actual})",
                "modificado_por": f"Secretaria ({self.usuario_actual})",
                "fecha_modificacion": ahora_str
            }
            d["turnos"].append(t_nuevo)
            d["auditoria"].append(f"[{ahora_str}] Turno creado por Secretaria {self.usuario_actual} para DNI {ec_dni.get()}")
            save_data(d)
            lbl_fb_c.config(text="¡Turno creado exitosamente por Secretaría!", fg="green")
            ec_nombre.delete(0, tk.END)
            ec_dni.delete(0, tk.END)
            ec_contacto.delete(0, tk.END)

        tk.Button(tab_crear, text="Guardar Turno en Agenda", bg="green", fg="white", font=("Arial", 10, "bold"), command=guardar_turno_sec).grid(row=5, column=0, pady=10)

        # ==================== PESTAÑA 2: MODIFICAR / CANCELAR ====================
        tab_modificar.columnconfigure(0, weight=1)
        tab_modificar.rowconfigure(1, weight=1)
        tk.Label(tab_modificar, text="Seleccione el turno a cancelar o reprogramar:", font=("Arial", 11, "bold")).grid(row=0, column=0, pady=5)

        listbox_mod = ListboxFrame(tab_modificar, row_idx=1)
        data = load_data()
        for idx, t in enumerate(data["turnos"]):
            alerta = " [⚠️ REPR.]" if t.get("requiere_nuevo_turno", False) else ""
            listbox_mod.lb.insert(tk.END, f"{idx+1}. Paciente: {t['paciente']} (DNI: {t.get('dni','N/A')}) | Fecha: {t['fecha']} | O.S.: {t['obra_social']} | Estado: {t['estado']}{alerta}")

        lbl_fb_m = tk.Label(tab_modificar, text="", font=("Arial", 9, "bold"))
        lbl_fb_m.grid(row=2, column=0, pady=2)

        def cancelar_turno():
            try:
                idx = listbox_mod.lb.curselection()[0]
                d = load_data()
                t_del = d["turnos"].pop(idx)
                ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                d["auditoria"].append(f"[{ahora_str}] Turno de {t_del['paciente']} cancelado por Secretaria {self.usuario_actual}")
                save_data(d)
                lbl_fb_m.config(text="Turno cancelado correctamente.", fg="green")
                self.secretary_view()
            except IndexError:
                lbl_fb_m.config(text="Aviso: Seleccione un turno de la lista.", fg="red")

        turno_a_repro = {"idx": None}
        def preparar_reprog():
            try:
                turno_a_repro["idx"] = listbox_mod.lb.curselection()[0]
                lbl_fb_m.config(text="Turno seleccionado. Elija la nueva fecha y hora abajo.", fg="blue")
            except IndexError:
                lbl_fb_m.config(text="Aviso: Seleccione un turno para reprogramar.", fg="red")

        btn_mod_box = tk.Frame(tab_modificar)
        btn_mod_box.grid(row=3, column=0, pady=5)
        tk.Button(btn_mod_box, text="1️⃣ Seleccionar para Reprogramar", bg="#f57c00", fg="white", command=preparar_reprog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_mod_box, text="❌ Cancelar Turno Seleccionado", bg="#d32f2f", fg="white", command=cancelar_turno).pack(side=tk.LEFT, padx=5)

        def ejecutar_reprog(nueva_fh):
            idx = turno_a_repro["idx"]
            if idx is None:
                lbl_fb_m.config(text="Error: Primero seleccione un turno con el botón naranja.", fg="red")
                return
            d = load_data()
            ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            d["turnos"][idx]["fecha"] = nueva_fh
            d["turnos"][idx]["estado"] = "Pendiente"
            d["turnos"][idx]["requiere_nuevo_turno"] = False
            d["turnos"][idx]["modificado_por"] = f"Secretaria ({self.usuario_actual})"
            d["turnos"][idx]["fecha_modificacion"] = ahora_str
            d["auditoria"].append(f"[{ahora_str}] Turno reprogramado por Secretaria {self.usuario_actual} para {nueva_fh}")
            save_data(d)
            lbl_fb_m.config(text="Turno reprogramado con éxito.", fg="green")
            self.secretary_view()

        self.crear_selector_horario_integrado(tab_modificar, ejecutar_reprog, row_idx=4)

        # ==================== PESTAÑA 3: INFORMACIÓN Y DETALLES (CON SCROLL DUAL) ====================
        tab_info.columnconfigure(0, weight=1)
        tab_info.rowconfigure(1, weight=1)
        tk.Label(tab_info, text="Seleccione un turno para ver su información y auditoría completa:", font=("Arial", 11, "bold")).grid(row=0, column=0, pady=5)

        listbox_info = ListboxFrame(tab_info, row_idx=1)
        for idx, t in enumerate(data["turnos"]):
            listbox_info.lb.insert(tk.END, f"{idx+1}. Paciente: {t['paciente']} | DNI: {t.get('dni','N/A')} | Fecha: {t['fecha']} | Estado: {t['estado']}")

        detalle_frame = tk.LabelFrame(tab_info, text=" 🔍 Información Detallada e Historial (Scroll Dual) ", padx=10, pady=10)
        detalle_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        detalle_frame.columnconfigure(0, weight=1)
        detalle_frame.rowconfigure(0, weight=1)

        txt_detalles_sec = self.crear_caja_texto_desplazable(detalle_frame, altura=7)

        def mostrar_detalles_sec(event):
            try:
                sel = listbox_info.lb.curselection()[0]
                t = data["turnos"][sel]
                historial_cambios = "\n".join([f"   • {reg}" for reg in data.get("auditoria", []) if t['paciente'] in reg or t.get('dni', '') in reg])
                if not historial_cambios:
                    historial_cambios = "   (Sin registros específicos de auditoría)"

                texto_detalles = (
                    f"========================================================================\n"
                    f" DATOS GENERALES DEL TURNO:\n"
                    f"========================================================================\n"
                    f" • Paciente: {t['paciente']} | DNI: {t.get('dni', 'N/A')} | Tel: {t.get('contacto', 'N/A')}\n"
                    f" • Obra Social: {t['obra_social']} (Afiliado: {t.get('afiliado', 'N/A')})\n"
                    f" • Fecha y Hora: {t['fecha']} | Estado: {t['estado']}\n\n"
                    f"========================================================================\n"
                    f" TRAZABILIDAD Y AUDITORÍA:\n"
                    f"========================================================================\n"
                    f" • Creado originalmente por: {t.get('creado_por', 'N/A')}\n"
                    f" • Última modificación por: {t.get('modificado_por', 'N/A')} el {t.get('fecha_modificacion', 'N/A')}\n\n"
                    f" • Historial de eventos:\n{historial_cambios}\n"
                    f"========================================================================\n"
                )
                txt_detalles_sec.config(state="normal")
                txt_detalles_sec.delete("1.0", tk.END)
                txt_detalles_sec.insert("1.0", texto_detalles)
                txt_detalles_sec.config(state="disabled")
            except IndexError:
                pass

        listbox_info.lb.bind('<<ListboxSelect>>', mostrar_detalles_sec)

        tk.Button(sec_frame, text="Cerrar Sesión / Volver al Menú Principal", bg="#c62828", fg="white", command=self.main_menu).grid(row=2, column=0, pady=10)

    # --- MÓDULO MÉDICO / SUPER ADMIN (MODULAR CON PESTAÑAS Y SCROLL DUAL) ---
    def doctor_view(self):
        self.clear_window()
        
        doc_frame = tk.Frame(self.root)
        doc_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        doc_frame.columnconfigure(0, weight=1)
        doc_frame.rowconfigure(1, weight=1)

        top_bar_doc = tk.Frame(doc_frame)
        top_bar_doc.grid(row=0, column=0, sticky="ew", pady=5)
        tk.Label(top_bar_doc, text=f"Panel Profesional & Super Admin - Dr. Salvador Amado ({self.usuario_actual})", font=("Arial", 13, "bold")).pack(side=tk.LEFT)
        tk.Button(top_bar_doc, text="🔑 Cambiar mi Contraseña", bg="#0288d1", fg="white", command=self.abrir_cambio_password).pack(side=tk.RIGHT)

        notebook_doc = ttk.Notebook(doc_frame)
        notebook_doc.grid(row=1, column=0, sticky="nsew", pady=5)

        tab_doc_agenda = tk.Frame(notebook_doc)
        tab_doc_info = tk.Frame(notebook_doc)
        tab_doc_admin = tk.Frame(notebook_doc)

        notebook_doc.add(tab_doc_agenda, text=" 🩺 Gestión de Turnos y Agenda ")
        notebook_doc.add(tab_doc_info, text=" 📋 Información y Detalles de Turnos ")
        notebook_doc.add(tab_doc_admin, text=" 🛡️ Super Admin y Auditoría de Perfiles ")

        data = load_data()

        # ==================== PESTAÑA 1: GESTIÓN DE TURNOS ====================
        tab_doc_agenda.columnconfigure(0, weight=1)
        tab_doc_agenda.rowconfigure(1, weight=1)
        tk.Label(tab_doc_agenda, text="Agenda Médica de Turnos:", font=("Arial", 11, "bold")).grid(row=0, column=0, pady=5)

        listbox_agenda_doc = ListboxFrame(tab_doc_agenda, row_idx=1)
        for t in data["turnos"]:
            dni_p = t.get('dni', 'N/A')
            visitas_totales = sum(1 for item in data["turnos"] if item.get('dni') == dni_p and item.get('estado') == 'Atendido')
            req = " (Requiere Reprog.)" if t.get("requiere_nuevo_turno", False) else ""
            listbox_agenda_doc.lb.insert(tk.END, f"Paciente: {t['paciente']} | DNI: {dni_p} (Visitas: {visitas_totales}) | Horario: {t['fecha']} | Estado: {t['estado']}{req}")

        lbl_status_doc = tk.Label(tab_doc_agenda, text="", font=("Arial", 9, "bold"))
        lbl_status_doc.grid(row=2, column=0, pady=2)

        def cambiar_estado(nuevo_estado):
            try:
                idx = listbox_agenda_doc.lb.curselection()[0]
                ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                data["turnos"][idx]["estado"] = nuevo_estado
                data["turnos"][idx]["modificado_por"] = f"Dr. Amado ({self.usuario_actual})"
                data["turnos"][idx]["fecha_modificacion"] = ahora_str
                data["auditoria"].append(f"[{ahora_str}] Turno cambiado a '{nuevo_estado}' por Dr. Amado")
                save_data(data)
                lbl_status_doc.config(text=f"Estado actualizado a: {nuevo_estado}", fg="green")
                self.doctor_view()
            except IndexError:
                lbl_status_doc.config(text="Aviso: Seleccione un turno de la lista.", fg="red")

        def marcar_requiere_nuevo():
            try:
                idx = listbox_agenda_doc.lb.curselection()[0]
                ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                data["turnos"][idx]["requiere_nuevo_turno"] = True
                data["turnos"][idx]["modificado_por"] = f"Dr. Amado ({self.usuario_actual})"
                data["turnos"][idx]["fecha_modificacion"] = ahora_str
                save_data(data)
                lbl_status_doc.config(text="Indicación guardada para secretaría.", fg="green")
                self.doctor_view()
            except IndexError:
                lbl_status_doc.config(text="Aviso: Seleccione un turno.", fg="red")

        frame_doc_btn = tk.Frame(tab_doc_agenda)
        frame_doc_btn.grid(row=3, column=0, pady=5)
        tk.Button(frame_doc_btn, text="Marcar Atendido", bg="green", fg="white", command=lambda: cambiar_estado("Atendido")).pack(side=tk.LEFT, padx=3)
        tk.Button(frame_doc_btn, text="Marcar Ausente", bg="orange", fg="white", command=lambda: cambiar_estado("Ausente")).pack(side=tk.LEFT, padx=3)
        tk.Button(frame_doc_btn, text="📌 Indicar Reprogramación", bg="#7b1fa2", fg="white", command=marcar_requiere_nuevo).pack(side=tk.LEFT, padx=3)

        # ==================== PESTAÑA 2: INFORMACIÓN Y DETALLES (CON SCROLL DUAL) ====================
        tab_doc_info.columnconfigure(0, weight=1)
        tab_doc_info.rowconfigure(1, weight=1)
        tk.Label(tab_doc_info, text="Seleccione un turno para examinar su historial clínico y de auditoría detallado:", font=("Arial", 11, "bold")).grid(row=0, column=0, pady=5)

        listbox_info_doc = ListboxFrame(tab_doc_info, row_idx=1)
        for idx, t in enumerate(data["turnos"]):
            listbox_info_doc.lb.insert(tk.END, f"{idx+1}. Paciente: {t['paciente']} | DNI: {t.get('dni','N/A')} | Fecha: {t['fecha']} | Estado: {t['estado']}")

        det_doc_frame = tk.LabelFrame(tab_doc_info, text=" 🔍 Reporte Detallado del Turno (Scroll Dual) ", padx=10, pady=10)
        det_doc_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        det_doc_frame.columnconfigure(0, weight=1)
        det_doc_frame.rowconfigure(0, weight=1)

        txt_detalles_doc = self.crear_caja_texto_desplazable(det_doc_frame, altura=7)

        def mostrar_detalles_doc(event):
            try:
                sel = listbox_info_doc.lb.curselection()[0]
                t = data["turnos"][sel]
                historial_cambios = "\n".join([f"   • {reg}" for reg in data.get("auditoria", []) if t['paciente'] in reg or t.get('dni', '') in reg])
                if not historial_cambios:
                    historial_cambios = "   (Sin registros específicos de auditoría)"

                texto_detalles = (
                    f"========================================================================\n"
                    f" DATOS GENERALES DEL TURNO:\n"
                    f"========================================================================\n"
                    f" • Paciente: {t['paciente']} | DNI: {t.get('dni', 'N/A')} | Tel: {t.get('contacto', 'N/A')}\n"
                    f" • Obra Social: {t['obra_social']} (Afiliado: {t.get('afiliado', 'N/A')})\n"
                    f" • Fecha y Hora: {t['fecha']} | Estado: {t['estado']}\n\n"
                    f"========================================================================\n"
                    f" TRAZABILIDAD Y AUDITORÍA:\n"
                    f"========================================================================\n"
                    f" • Creado originalmente por: {t.get('creado_por', 'N/A')}\n"
                    f" • Última modificación por: {t.get('modificado_por', 'N/A')} el {t.get('fecha_modificacion', 'N/A')}\n\n"
                    f" • Historial completo:\n{historial_cambios}\n"
                    f"========================================================================\n"
                )
                txt_detalles_doc.config(state="normal")
                txt_detalles_doc.delete("1.0", tk.END)
                txt_detalles_doc.insert("1.0", texto_detalles)
                txt_detalles_doc.config(state="disabled")
            except IndexError:
                pass

        listbox_info_doc.lb.bind('<<ListboxSelect>>', mostrar_detalles_doc)

        # ==================== PESTAÑA 3: SUPER ADMIN Y AUDITORÍA DE PERFILES ====================
        tab_doc_admin.columnconfigure(0, weight=1)
        tab_doc_admin.rowconfigure(2, weight=1)

        tk.Label(tab_doc_admin, text="Gestión Avanzada de Perfiles, Credenciales y Auditoría de Usuarios", font=("Arial", 11, "bold")).grid(row=0, column=0, pady=5)

        listbox_users = ListboxFrame(tab_doc_admin, row_idx=1)
        listbox_users.lb.config(height=4)
        for idx, u in enumerate(data["usuarios"]):
            listbox_users.lb.insert(tk.END, f"[{idx}] Usuario: {u['usuario']} | Rol: {u['rol']} | Pass: {u['pass']}")

        form_admin = tk.Frame(tab_doc_admin)
        form_admin.grid(row=2, column=0, sticky="ew", padx=10, pady=3)
        form_admin.columnconfigure(1, weight=1)

        tk.Label(form_admin, text="Nuevo Nombre / Usuario:").grid(row=0, column=0, sticky="w", pady=2)
        e_edit_u = tk.Entry(form_admin, width=25)
        e_edit_u.grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(form_admin, text="Nueva Contraseña:").grid(row=1, column=0, sticky="w", pady=2)
        e_edit_p = tk.Entry(form_admin, width=25)
        e_edit_p.grid(row=1, column=1, sticky="w", pady=2)

        lbl_status_admin = tk.Label(tab_doc_admin, text="", font=("Arial", 9, "bold"))
        lbl_status_admin.grid(row=3, column=0, pady=2)

        def modificar_usuario():
            try:
                idx = listbox_users.lb.curselection()[0]
                d = load_data()
                nuevo_nombre = e_edit_u.get().strip()
                nueva_pass = e_edit_p.get().strip()

                if not nuevo_nombre or not nueva_pass:
                    lbl_status_admin.config(text="Error: Complete nombre y contraseña para modificar.", fg="red")
                    return

                old_name = d["usuarios"][idx]["usuario"]
                d["usuarios"][idx]["usuario"] = nuevo_nombre
                d["usuarios"][idx]["pass"] = nueva_pass
                ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                d["auditoria"].append(f"[{ahora_str}] SUPER ADMIN: Perfil de usuario '{old_name}' modificado a '{nuevo_nombre}' (Pass actualizada) por Dr. Amado")
                save_data(d)
                lbl_status_admin.config(text="Perfil y credenciales modificados con éxito.", fg="green")
                self.doctor_view()
            except IndexError:
                lbl_status_admin.config(text="Aviso: Seleccione un usuario de la lista superior.", fg="red")

        def agregar_usuario():
            nuevo_nombre = e_edit_u.get().strip()
            nueva_pass = e_edit_p.get().strip()
            if not nuevo_nombre or not nueva_pass:
                lbl_status_admin.config(text="Error: Complete usuario y contraseña.", fg="red")
                return
            d = load_data()
            d["usuarios"].append({"usuario": nuevo_nombre, "pass": nueva_pass, "rol": "Secretaria"})
            ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            d["auditoria"].append(f"[{ahora_str}] SUPER ADMIN: Creado nuevo perfil de secretaria '{nuevo_nombre}' por Dr. Amado")
            save_data(d)
            lbl_status_admin.config(text="Secretaria agregada con éxito.", fg="green")
            self.doctor_view()

        def eliminar_usuario():
            try:
                idx = listbox_users.lb.curselection()[0]
                d = load_data()
                usr = d["usuarios"][idx]
                if usr["rol"] == "Médico":
                    lbl_status_admin.config(text="Error: No se puede eliminar al médico principal.", fg="red")
                    return
                d["usuarios"].pop(idx)
                ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                d["auditoria"].append(f"[{ahora_str}] SUPER ADMIN: Eliminado perfil de usuario '{usr['usuario']}' por Dr. Amado")
                save_data(d)
                lbl_status_admin.config(text="Usuario eliminado del sistema.", fg="green")
                self.doctor_view()
            except IndexError:
                lbl_status_admin.config(text="Aviso: Seleccione un usuario.", fg="red")

        def limpiar_base_datos():
            d = load_data()
            d["turnos"] = []
            d["bloqueos"] = []
            ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            d["auditoria"].append(f"[{ahora_str}] SUPER ADMIN: Base de datos limpiada (turnos y registros de auditoría blanqueados) por Dr. Amado")
            save_data(d)
            lbl_status_admin.config(text="¡Base de datos de turnos limpiada con éxito!", fg="green")
            self.root.after(1200, self.doctor_view)

        btn_admin_frame = tk.Frame(tab_doc_admin)
        btn_admin_frame.grid(row=4, column=0, pady=5)
        tk.Button(btn_admin_frame, text="✏️ Modificar Credenciales", bg="#f57c00", fg="white", command=modificar_usuario).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_admin_frame, text="➕ Agregar Secretaria", bg="#0288d1", fg="white", command=agregar_usuario).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_admin_frame, text="🗑️ Eliminar Perfil", bg="#d32f2f", fg="white", command=eliminar_usuario).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_admin_frame, text="⚠️ Limpiar Base de Datos", bg="#b71c1c", fg="white", command=limpiar_base_datos).pack(side=tk.LEFT, padx=3)

        aud_frame = tk.LabelFrame(tab_doc_admin, text=" 📜 Historial de Auditoría de Perfiles y Seguridad ", padx=10, pady=5)
        aud_frame.grid(row=5, column=0, sticky="nsew", padx=5, pady=5)
        aud_frame.columnconfigure(0, weight=1)
        aud_frame.rowconfigure(0, weight=1)

        txt_auditoria_perfiles = self.crear_caja_texto_desplazable(aud_frame, altura=5)
        
        registros_seguridad = [reg for reg in data.get("auditoria", []) if "SUPER ADMIN" in reg or "Contraseña cambiada" in reg]
        texto_seguridad_full = "\n".join([f"   • {r}" for r in registros_seguridad])
        if not texto_seguridad_full:
            texto_seguridad_full = "   (Sin registros de cambios en perfiles aún)"

        txt_auditoria_perfiles.config(state="normal")
        txt_auditoria_perfiles.delete("1.0", tk.END)
        txt_auditoria_perfiles.insert("1.0", texto_seguridad_full)
        txt_auditoria_perfiles.config(state="disabled")

        tk.Button(doc_frame, text="Cerrar Sesión / Volver al Menú Principal", bg="#c62828", fg="white", command=self.main_menu).grid(row=2, column=0, pady=10)


class ListboxFrame(tk.Frame):
    def __init__(self, parent, row_idx=0):
        super().__init__(parent)
        self.grid(row=row_idx, column=0, sticky="nsew", pady=3)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.lb = tk.Listbox(self, width=120, height=8, font=("Consolas", 10))
        self.lb.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.lb.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.lb.config(yscrollcommand=scrollbar.set)


if __name__ == "__main__":
    root = tk.Tk()
    app = ConsultorioApp(root)
    root.mainloop()