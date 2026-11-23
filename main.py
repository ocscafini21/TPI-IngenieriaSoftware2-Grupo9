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
                {"usuario": "amado", "pass": "medico2026", "rol": "Médico"},
            ],
            "obras_sociales": [
                "Particular (Sin Cobertura)",
                "OSDE",
                "Swiss Medical",
                "Galeno",
                "IOMA",
                "PAMI",
                "Medicus",
                "OMINT",
                "Luis Pasteur",
                "Sancor Salud",
                "Accord Salud",
            ],
            "bloqueos": [],
            "auditoria": [],
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def load_data():
    if not os.path.exists(DATA_FILE):
        init_db()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
        data.setdefault("turnos", [])
        data.setdefault(
            "usuarios",
            [
                {"usuario": "admin", "pass": "1234", "rol": "Secretaria"},
                {"usuario": "amado", "pass": "medico2026", "rol": "Médico"},
            ],
        )
        data.setdefault(
            "obras_sociales",
            [
                "Particular (Sin Cobertura)",
                "OSDE",
                "Swiss Medical",
                "Galeno",
                "IOMA",
                "PAMI",
                "Medicus",
                "OMINT",
                "Luis Pasteur",
                "Sancor Salud",
                "Accord Salud",
            ],
        )
        data.setdefault("bloqueos", [])
        data.setdefault("auditoria", [])
        return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


class ConsultorioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión - Consultorio Dr. Salvador Amado")
        self.root.geometry("980x820")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        init_db()
        self.usuario_actual = None
        self.rol_actual = None
        self.puesto_configurado = None
        self.selector_interfaz()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def boton_volver_interfaz(self, parent, texto="↩️ Volver atrás (Elegir interfaz)"):
        return tk.Button(
            parent,
            text=texto,
            bg="#eceff1",
            fg="#263238",
            command=self.selector_interfaz,
        )

    def crear_caja_texto_desplazable(self, parent, height=8):
        container = tk.Frame(parent)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        txt = tk.Text(
            container,
            wrap="none",
            font=("Consolas", 10),
            bg="#f9f9f9",
            fg="#222222",
            height=height,
        )
        txt.grid(row=0, column=0, sticky="nsew")

        scroll_y = tk.Scrollbar(container, orient="vertical", command=txt.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")

        scroll_x = tk.Scrollbar(container, orient="horizontal", command=txt.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")

        txt.config(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        txt.config(state="disabled")
        return txt

    def escribir_texto_protegido(self, txt_widget, contenido):
        txt_widget.config(state="normal")
        txt_widget.delete("1.0", tk.END)
        txt_widget.insert("1.0", contenido)
        txt_widget.config(state="disabled")

    def validar_datos_paciente(self, nombre, dni, contacto, lbl_estado):
        if not nombre or not dni or not contacto:
            lbl_estado.config(
                text="Error: Complete Nombre y Apellido, DNI y Teléfono.", fg="#c62828"
            )
            return False
        if not dni.isdigit() or len(dni) < 6:
            lbl_estado.config(
                text="Error: El DNI debe contener solo números (mínimo 6 dígitos).",
                fg="#c62828",
            )
            return False
        tel_limpio = contacto.replace("-", "").replace(" ", "").replace("+", "")
        if not tel_limpio.isdigit() or len(tel_limpio) < 6:
            lbl_estado.config(
                text="Error: Ingrese un teléfono de contacto válido.", fg="#c62828"
            )
            return False
        return True

    def separar_auditoria_turno_y_perfil(self, turno, auditoria_lista, usuario_perfil):
        paciente = str(turno.get("paciente", "")).strip()
        dni = str(turno.get("dni", "")).strip()

        historial_turno = []
        historial_perfil = []

        for reg in auditoria_lista:
            reg_str = str(reg)
            es_evento_perfil = (
                "contraseña" in reg_str.lower()
                or "perfil" in reg_str.lower()
                or "usuario" in reg_str.lower()
                or "super admin" in reg_str.lower()
            )
            coincide_turno = (paciente and f" {paciente} " in f" {reg_str} ") or (
                dni and dni in reg_str
            )

            if coincide_turno and not es_evento_perfil:
                historial_turno.append(f"   • {reg_str}")
            elif usuario_perfil and usuario_perfil in reg_str and es_evento_perfil:
                historial_perfil.append(f"   • {reg_str}")

        return historial_turno, historial_perfil

    # --- PANTALLA INICIAL: SELECCIÓN DE INTERFAZ DEL PUESTO ---
    def selector_interfaz(self):
        self.usuario_actual = None
        self.rol_actual = None
        self.puesto_configurado = None
        self.clear_window()

        frame_main = tk.Frame(self.root, padx=20, pady=20)
        frame_main.grid(row=0, column=0, sticky="nsew")

        tk.Label(
            frame_main,
            text="Clínica Médica - Dr. Salvador Amado",
            font=("Arial", 16, "bold"),
        ).pack(pady=15)
        tk.Label(
            frame_main,
            text="Seleccione qué interfaz desea mostrar en esta pantalla:",
            font=("Arial", 11, "italic"),
        ).pack(pady=5)

        tk.Button(
            frame_main,
            text="👤 Interfaz Paciente (Autogestión de Turnos)",
            width=50,
            height=2,
            bg="#e1f5fe",
            command=lambda: self.iniciar_puesto("paciente"),
        ).pack(pady=10)

        tk.Button(
            frame_main,
            text="👩‍💼 Interfaz Secretaría (Administración)",
            width=50,
            height=2,
            bg="#e8f5e9",
            command=lambda: self.iniciar_puesto("secretaria"),
        ).pack(pady=10)

        tk.Button(
            frame_main,
            text="🩺 Interfaz Médico / Super Admin (Dr. Amado)",
            width=50,
            height=2,
            bg="#fff3e0",
            command=lambda: self.iniciar_puesto("medico"),
        ).pack(pady=10)

        tk.Button(
            frame_main,
            text="❌ Cerrar Aplicación",
            width=25,
            command=self.root.quit,
        ).pack(pady=20)

    def iniciar_puesto(self, puesto):
        self.puesto_configurado = puesto
        if puesto == "paciente":
            self.patient_view()
        elif puesto == "secretaria":
            self.login_view("Secretaria")
        elif puesto == "medico":
            self.login_view("Médico")

    # --- LOGIN ---
    def login_view(self, rol_requerido):
        self.usuario_actual = None
        self.rol_actual = None
        self.clear_window()

        frame_login = tk.Frame(self.root, padx=20, pady=20)
        frame_login.grid(row=0, column=0, sticky="nsew")

        tk.Label(
            frame_login,
            text=f"Acceso Restringido - Interfaz {rol_requerido}",
            font=("Arial", 14, "bold"),
        ).pack(pady=15)

        tk.Label(frame_login, text="Usuario:").pack()
        e_user = tk.Entry(frame_login, width=30)
        e_user.pack(pady=5)

        tk.Label(frame_login, text="Contraseña:").pack()
        e_pass = tk.Entry(frame_login, width=30, show="*")
        e_pass.pack(pady=5)

        lbl_error = tk.Label(frame_login, text="", font=("Arial", 9, "bold"), fg="#c62828")
        lbl_error.pack(pady=5)

        def validar_ingreso():
            data = load_data()
            usuario_ingresado = e_user.get().strip()
            pass_ingresada = e_pass.get()

            for u in data["usuarios"]:
                if (
                    u["usuario"] == usuario_ingresado
                    and u["pass"] == pass_ingresada
                    and u["rol"] == rol_requerido
                ):
                    self.usuario_actual = usuario_ingresado
                    self.rol_actual = rol_requerido
                    if rol_requerido == "Secretaria":
                        self.secretary_view()
                    else:
                        self.doctor_view()
                    return
            lbl_error.config(text="Usuario, contraseña o rol incorrectos.")

        tk.Button(
            frame_login,
            text="Ingresar",
            bg="green",
            fg="white",
            width=20,
            command=validar_ingreso,
        ).pack(pady=10)

        self.boton_volver_interfaz(frame_login).pack(pady=5)

    # --- SELECTOR DE HORARIO INTEGRADO ---
    def crear_selector_horario_integrado(self, parent_frame, callback_asignar, lbl_feedback):
        frame_selector = tk.LabelFrame(
            parent_frame,
            text=" 📅 Selector de Fecha y Horario ",
            padx=10,
            pady=8,
        )
        frame_selector.pack(pady=8, fill="x", padx=10)

        fila_top = tk.Frame(frame_selector)
        fila_top.pack(fill="x", pady=2)

        tk.Label(
            fila_top, text="Fecha (DD/MM/AAAA):", font=("Arial", 9, "bold")
        ).pack(side=tk.LEFT)
        e_fecha = tk.Entry(fila_top, width=14)
        e_fecha.pack(side=tk.LEFT, padx=6)
        e_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))

        lbl_disp = tk.Label(
            frame_selector,
            text="Estado del horario: elija una fecha hábil y un horario libre.",
            font=("Arial", 9, "italic"),
            fg="#37474f",
        )
        lbl_disp.pack(anchor="w", pady=(4, 2))

        horarios_base = []
        for h in range(8, 16):
            horarios_base.append(f"{h:02d}:00")
            if h < 16:
                horarios_base.append(f"{h:02d}:30")

        listbox_horas = tk.Listbox(
            frame_selector, width=42, height=6, exportselection=False
        )
        listbox_horas.pack(pady=4)

        estado_sel = {"hora_confirmada": "", "ultima_hora_marcada": ""}

        def refrescar_lista_horas(*_):
            fecha_txt = e_fecha.get().strip()
            data = load_data()
            ocupados = {
                t["fecha"]
                for t in data["turnos"]
                if t.get("fecha", "").startswith(f"{fecha_txt} - ")
            }
            listbox_horas.delete(0, tk.END)
            for hora in horarios_base:
                etiqueta_fh = f"{fecha_txt} - {hora} hs"
                if etiqueta_fh in ocupados:
                    listbox_horas.insert(tk.END, f"{hora}  [OCUPADO]")
                else:
                    listbox_horas.insert(tk.END, f"{hora}  [DISPONIBLE]")

        refrescar_lista_horas()
        e_fecha.bind("<KeyRelease>", refrescar_lista_horas)

        def validar_y_asignar(mostrar_aviso_exito=True):
            fecha_str = e_fecha.get().strip()

            try:
                dt_fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
                if dt_fecha.weekday() > 4:
                    lbl_feedback.config(
                        text="Error: El consultorio solo atiende de Lunes a Viernes.",
                        fg="#c62828",
                    )
                    lbl_disp.config(
                        text="Día no hábil (solo Lunes a Viernes).", fg="#c62828"
                    )
                    return ""
            except ValueError:
                lbl_feedback.config(
                    text="Error: Formato de fecha inválido. Use DD/MM/AAAA.",
                    fg="#c62828",
                )
                lbl_disp.config(text="Formato de fecha inválido.", fg="#c62828")
                return ""

            sel = listbox_horas.curselection()
            if sel:
                item_texto = listbox_horas.get(sel[0])
                hora_limpia = item_texto.split("  [")[0].strip()
                estado_sel["ultima_hora_marcada"] = hora_limpia
            elif estado_sel["ultima_hora_marcada"]:
                hora_limpia = estado_sel["ultima_hora_marcada"]
            else:
                lbl_feedback.config(
                    text="Aviso: Haga clic en un horario de la lista.",
                    fg="#c62828",
                )
                lbl_disp.config(text="No hay ningún horario seleccionado.", fg="#c62828")
                return ""

            fecha_hora_completa = f"{fecha_str} - {hora_limpia} hs"

            data = load_data()
            if any(t.get("fecha") == fecha_hora_completa for t in data["turnos"]):
                refrescar_lista_horas()
                lbl_feedback.config(
                    text="Conflicto: Este horario ya se encuentra ocupado.",
                    fg="#c62828",
                )
                lbl_disp.config(
                    text=f"{hora_limpia} está OCUPADO para el {fecha_str}.",
                    fg="#c62828",
                )
                return ""

            dt_completo = datetime.strptime(
                f"{fecha_str} {hora_limpia}", "%d/%m/%Y %H:%M"
            )
            if dt_completo < datetime.now():
                lbl_feedback.config(
                    text="Error Temporal: No se puede seleccionar una fecha u horario pasado / ya transcurrido.",
                    fg="#c62828",
                )
                lbl_disp.config(
                    text=f"{hora_limpia} ya pasó o corresponde a una fecha pasada.",
                    fg="#c62828",
                )
                return ""

            estado_sel["hora_confirmada"] = fecha_hora_completa
            callback_asignar(fecha_hora_completa)
            lbl_disp.config(
                text=f"Horario {fecha_hora_completa} DISPONIBLE y seleccionado.",
                fg="#2e7d32",
            )
            if mostrar_aviso_exito:
                lbl_feedback.config(
                    text=f"Horario confirmado: {fecha_hora_completa}. Ahora puede confirmar la reserva.",
                    fg="#1565c0",
                )
            return fecha_hora_completa

        def on_select_hora(_event):
            sel = listbox_horas.curselection()
            if not sel:
                return
            item_texto = listbox_horas.get(sel[0])
            hora_limpia = item_texto.split("  [")[0].strip()
            estado_sel["ultima_hora_marcada"] = hora_limpia
            fecha_str = e_fecha.get().strip()
            if "[OCUPADO]" in item_texto:
                lbl_disp.config(
                    text=f"{hora_limpia} del {fecha_str} figura como OCUPADO.",
                    fg="#c62828",
                )
            else:
                lbl_disp.config(
                    text=f"{hora_limpia} del {fecha_str} está DISPONIBLE. Presione 'Confirmar este Horario' o 'Confirmar Reserva'.",
                    fg="#2e7d32",
                )

        listbox_horas.bind("<<ListboxSelect>>", on_select_hora)

        tk.Button(
            frame_selector,
            text="Confirmar este Horario",
            bg="#0288d1",
            fg="white",
            command=lambda: validar_y_asignar(True),
        ).pack(pady=5)

        return validar_y_asignar

    # --- INTERFAZ DE PACIENTE ---
    def patient_view(self):
        self.clear_window()

        frame_pac = tk.Frame(self.root, padx=15, pady=10)
        frame_pac.grid(row=0, column=0, sticky="nsew")

        frame_top = tk.Frame(frame_pac)
        frame_top.pack(fill="x", pady=2)
        self.boton_volver_interfaz(frame_top).pack(side=tk.LEFT)

        tk.Label(
            frame_pac,
            text="Portal de Autogestión - Paciente",
            font=("Arial", 14, "bold"),
        ).pack(pady=5)

        frame_form = tk.Frame(frame_pac)
        frame_form.pack(pady=4)

        tk.Label(frame_form, text="Nombre y Apellido:").grid(
            row=0, column=0, sticky="w", pady=2
        )
        e_nombre = tk.Entry(frame_form, width=35)
        e_nombre.grid(row=0, column=1, pady=2)

        tk.Label(frame_form, text="DNI:").grid(row=1, column=0, sticky="w", pady=2)
        e_dni = tk.Entry(frame_form, width=35)
        e_dni.grid(row=1, column=1, pady=2)

        tk.Label(frame_form, text="Teléfono de Contacto:").grid(
            row=2, column=0, sticky="w", pady=2
        )
        e_contacto = tk.Entry(frame_form, width=35)
        e_contacto.grid(row=2, column=1, pady=2)

        tk.Label(frame_form, text="Cobertura / Obra Social:").grid(
            row=3, column=0, sticky="w", pady=2
        )
        data_init = load_data()
        combo_os = ttk.Combobox(
            frame_form,
            values=data_init["obras_sociales"],
            width=33,
            state="readonly",
        )
        combo_os.grid(row=3, column=1, pady=2)
        combo_os.current(0)

        tk.Label(frame_form, text="Número de Afiliado:").grid(
            row=4, column=0, sticky="w", pady=2
        )
        e_afiliado = tk.Entry(frame_form, width=35)
        e_afiliado.grid(row=4, column=1, pady=2)
        e_afiliado.insert(0, "Particular / Sin credencial")

        lbl_turno = tk.Label(
            frame_pac,
            text="Turno seleccionado: [Ninguno]",
            font=("Arial", 10, "bold"),
            fg="#1565c0",
        )
        lbl_turno.pack(pady=3)

        lbl_estado_pac = tk.Label(
            frame_pac, text="", font=("Arial", 9, "bold"), fg="#2e7d32"
        )
        lbl_estado_pac.pack(pady=2)

        turno_seleccionado = {"val": ""}

        def asignar_horario_paciente(fh):
            turno_seleccionado["val"] = fh
            lbl_turno.config(text=f"Turno seleccionado: {fh}")

        validar_horario_fn = self.crear_selector_horario_integrado(
            frame_pac, asignar_horario_paciente, lbl_estado_pac
        )

        def reservar():
            nombre = e_nombre.get().strip()
            dni = e_dni.get().strip()
            contacto = e_contacto.get().strip()

            if not self.validar_datos_paciente(nombre, dni, contacto, lbl_estado_pac):
                return

            if not turno_seleccionado["val"]:
                fh_auto = validar_horario_fn(False)
                if not fh_auto:
                    return

            data = load_data()
            for t in data["turnos"]:
                if t["fecha"] == turno_seleccionado["val"]:
                    lbl_estado_pac.config(
                        text="Conflicto: Este horario ya se encuentra ocupado.",
                        fg="#c62828",
                    )
                    return

            ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            nuevo_turno = {
                "paciente": nombre,
                "dni": dni,
                "contacto": contacto,
                "fecha": turno_seleccionado["val"],
                "obra_social": combo_os.get(),
                "afiliado": e_afiliado.get().strip(),
                "estado": "Pendiente",
                "requiere_nuevo_turno": False,
                "creado_por": f"Autogestión Paciente ({nombre})",
                "modificado_por": f"Autogestión Paciente ({nombre})",
                "fecha_modificacion": ahora_str,
            }
            data["turnos"].append(nuevo_turno)
            data["auditoria"].append(
                f"[{ahora_str}] Turno creado por Paciente {nombre} (DNI {dni}) para {turno_seleccionado['val']}"
            )
            save_data(data)

            e_nombre.delete(0, tk.END)
            e_dni.delete(0, tk.END)
            e_contacto.delete(0, tk.END)
            combo_os.current(0)
            e_afiliado.delete(0, tk.END)
            e_afiliado.insert(0, "Particular / Sin credencial")
            turno_seleccionado["val"] = ""
            lbl_turno.config(text="Turno seleccionado: [Ninguno]")
            lbl_estado_pac.config(
                text="¡Turno reservado correctamente! Pantalla lista para el próximo paciente.",
                fg="#2e7d32",
            )
            self.patient_view()

        tk.Button(
            frame_pac,
            text="Confirmar Reserva de Turno",
            bg="green",
            fg="white",
            font=("Arial", 10, "bold"),
            command=reservar,
        ).pack(pady=8)

    # --- CAMBIO DE CONTRASEÑA PROPIO ---
    def abrir_cambio_password(self):
        win_pass = tk.Toplevel(self.root)
        win_pass.title(f"Cambiar Contraseña - {self.usuario_actual}")
        win_pass.geometry("360x240")

        tk.Label(win_pass, text="Contraseña Actual:").pack(pady=5)
        e_actual = tk.Entry(win_pass, show="*", width=25)
        e_actual.pack(pady=2)

        tk.Label(win_pass, text="Nueva Contraseña:").pack(pady=5)
        e_nueva = tk.Entry(win_pass, show="*", width=25)
        e_nueva.pack(pady=2)

        lbl_msg = tk.Label(win_pass, text="", font=("Arial", 9, "bold"))
        lbl_msg.pack(pady=5)

        def guardar_cambio():
            data = load_data()
            pass_act = e_actual.get()
            pass_nue = e_nueva.get()

            if not pass_act or not pass_nue:
                lbl_msg.config(text="Complete ambos campos.", fg="#c62828")
                return

            for u in data["usuarios"]:
                if u["usuario"] == self.usuario_actual:
                    if u["pass"] == pass_act:
                        u["pass"] = pass_nue
                        ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                        data["auditoria"].append(
                            f"[{ahora_str}] Perfil '{self.usuario_actual}' cambió su contraseña."
                        )
                        save_data(data)
                        lbl_msg.config(
                            text="Contraseña actualizada correctamente.", fg="#2e7d32"
                        )
                        self.root.after(900, win_pass.destroy)
                        return
                    lbl_msg.config(
                        text="La contraseña actual es incorrecta.", fg="#c62828"
                    )
                    return

        tk.Button(
            win_pass,
            text="Guardar Nueva Contraseña",
            bg="green",
            fg="white",
            command=guardar_cambio,
        ).pack(pady=10)

    # --- INTERFAZ DE SECRETARIA CON HISTORIAL DE TURNO Y DE PERFIL SEPARADOS ---
    def secretary_view(self):
        self.clear_window()
        frame_sec = tk.Frame(self.root, padx=12, pady=10)
        frame_sec.grid(row=0, column=0, sticky="nsew")
        frame_sec.columnconfigure(0, weight=1)
        frame_sec.rowconfigure(1, weight=1)

        header = tk.Frame(frame_sec)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        tk.Label(
            header,
            text=f"Panel Administrativo - Secretaria ({self.usuario_actual})",
            font=("Arial", 13, "bold"),
        ).pack(side=tk.LEFT)
        tk.Button(
            header,
            text="🔑 Cambiar mi Contraseña",
            bg="#0288d1",
            fg="white",
            command=self.abrir_cambio_password,
        ).pack(side=tk.RIGHT)

        notebook = ttk.Notebook(frame_sec)
        notebook.grid(row=1, column=0, sticky="nsew")

        tab_gestion = tk.Frame(notebook, padx=10, pady=10)
        tab_info = tk.Frame(notebook, padx=10, pady=10)
        tab_info.columnconfigure(0, weight=1)
        tab_info.rowconfigure(2, weight=3)
        tab_info.rowconfigure(3, weight=2)

        notebook.add(tab_gestion, text=" 📅 Gestión / Reprogramación ")
        notebook.add(tab_info, text=" 📋 Detalles e Historial (Scroll Dual) ")

        lbl_estado_sec = tk.Label(
            tab_gestion, text="", font=("Arial", 9, "bold"), fg="#2e7d32"
        )
        lbl_estado_sec.pack(pady=2)

        filtro_frame = tk.Frame(tab_gestion)
        filtro_frame.pack(fill="x", pady=2)
        tk.Label(filtro_frame, text="Buscar (Paciente o DNI):").pack(side=tk.LEFT)
        e_buscar = tk.Entry(filtro_frame, width=28)
        e_buscar.pack(side=tk.LEFT, padx=6)

        listbox = tk.Listbox(tab_gestion, width=115, height=7, exportselection=False)
        listbox.pack(pady=4, fill="x")

        indices_visibles = []

        def cargar_turnos_sec():
            indices_visibles.clear()
            listbox.delete(0, tk.END)
            data = load_data()
            q = e_buscar.get().strip().lower()
            for idx, t in enumerate(data["turnos"]):
                texto_busqueda = (
                    f"{t.get('paciente', '')} {t.get('dni', '')}".lower()
                )
                if q and q not in texto_busqueda:
                    continue
                indices_visibles.append(idx)
                alerta = (
                    " [⚠️ REPROGRAMAR]"
                    if t.get("requiere_nuevo_turno", False)
                    else ""
                )
                mod = f" (Modif: {t.get('modificado_por', 'N/A')})"
                listbox.insert(
                    tk.END,
                    f"{len(indices_visibles)}. Paciente: {t['paciente']} (DNI: {t.get('dni','N/A')}) | Fecha: {t['fecha']} | O.S.: {t['obra_social']} | Estado: {t['estado']}{alerta}{mod}",
                )

        e_buscar.bind("<KeyRelease>", lambda _e: cargar_turnos_sec())
        cargar_turnos_sec()

        turno_a_reprogramar = {"idx": None}

        def preparar_reprogramacion():
            try:
                sel_pos = listbox.curselection()[0]
                idx_real = indices_visibles[sel_pos]
                turno_a_reprogramar["idx"] = idx_real
                data = load_data()
                lbl_estado_sec.config(
                    text=f"Seleccionado para reprogramar: {data['turnos'][idx_real]['paciente']} ({data['turnos'][idx_real]['fecha']}). Elija nuevo horario abajo.",
                    fg="#ef6c00",
                )
            except IndexError:
                lbl_estado_sec.config(
                    text="Aviso: Seleccione un turno de la lista.", fg="#ef6c00"
                )

        def cancelar_turno():
            try:
                sel_pos = listbox.curselection()[0]
                idx_real = indices_visibles[sel_pos]
                data = load_data()
                t_eliminado = data["turnos"].pop(idx_real)
                ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                data["auditoria"].append(
                    f"[{ahora_str}] Turno de {t_eliminado['paciente']} (DNI {t_eliminado.get('dni','N/A')}) cancelado por Secretaria {self.usuario_actual}"
                )
                save_data(data)
                turno_a_reprogramar["idx"] = None
                cargar_turnos_sec()
                cargar_turnos_info()
                lbl_estado_sec.config(
                    text=f"Turno de {t_eliminado['paciente']} cancelado y cupo liberado.",
                    fg="#2e7d32",
                )
            except IndexError:
                lbl_estado_sec.config(
                    text="Aviso: Seleccione un turno para cancelar.", fg="#ef6c00"
                )

        frame_acciones = tk.Frame(tab_gestion)
        frame_acciones.pack(pady=4)
        tk.Button(
            frame_acciones,
            text="1️⃣ Seleccionar Turno a Reprogramar",
            bg="#f57c00",
            fg="white",
            command=preparar_reprogramacion,
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            frame_acciones,
            text="❌ Cancelar Turno Seleccionado",
            bg="#d32f2f",
            fg="white",
            command=cancelar_turno,
        ).pack(side=tk.LEFT, padx=5)

        def ejecutar_reprogramacion(nueva_fecha_hora):
            idx = turno_a_reprogramar["idx"]
            if idx is None:
                lbl_estado_sec.config(
                    text="Error: Primero seleccione un turno y presione 'Seleccionar Turno a Reprogramar'.",
                    fg="#c62828",
                )
                return
            data_fresh = load_data()
            for i, t in enumerate(data_fresh["turnos"]):
                if i != idx and t["fecha"] == nueva_fecha_hora:
                    lbl_estado_sec.config(
                        text="Conflicto: Ese nuevo horario ya está ocupado.",
                        fg="#c62828",
                    )
                    return

            ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            data_fresh["turnos"][idx]["fecha"] = nueva_fecha_hora
            data_fresh["turnos"][idx]["estado"] = "Pendiente"
            data_fresh["turnos"][idx]["requiere_nuevo_turno"] = False
            data_fresh["turnos"][idx][
                "modificado_por"
            ] = f"Secretaria ({self.usuario_actual})"
            data_fresh["turnos"][idx]["fecha_modificacion"] = ahora_str
            data_fresh["auditoria"].append(
                f"[{ahora_str}] Turno de {data_fresh['turnos'][idx]['paciente']} (DNI {data_fresh['turnos'][idx].get('dni','N/A')}) reprogramado por Secretaria {self.usuario_actual} para {nueva_fecha_hora}"
            )
            save_data(data_fresh)
            turno_a_reprogramar["idx"] = None
            cargar_turnos_sec()
            cargar_turnos_info()
            lbl_estado_sec.config(
                text=f"Turno reprogramado con éxito para {nueva_fecha_hora}.",
                fg="#2e7d32",
            )

        self.crear_selector_horario_integrado(
            tab_gestion, ejecutar_reprogramacion, lbl_estado_sec
        )

        tk.Label(
            tab_info,
            text="Seleccione un turno para ver su historial propio y, por separado, la auditoría del perfil de Secretaría:",
            font=("Arial", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        listbox_info = tk.Listbox(tab_info, width=115, height=5, exportselection=False)
        listbox_info.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        # Bloque 1: Info e historial exclusivo del turno seleccionado
        detalle_turno_frame = tk.LabelFrame(
            tab_info, text=" 🔍 Detalle e Historial del Turno Seleccionado ", padx=8, pady=6
        )
        detalle_turno_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 6))
        txt_detalles_turno = self.crear_caja_texto_desplazable(
            detalle_turno_frame, height=8
        )

        # Bloque 2: Historial separado del perfil de secretaría
        detalle_perfil_frame = tk.LabelFrame(
            tab_info,
            text=f" 👤 Auditoría del Perfil de Secretaría ({self.usuario_actual}) ",
            padx=8,
            pady=6,
        )
        detalle_perfil_frame.grid(row=3, column=0, sticky="nsew")
        txt_detalles_perfil = self.crear_caja_texto_desplazable(
            detalle_perfil_frame, height=5
        )

        def cargar_turnos_info():
            listbox_info.delete(0, tk.END)
            data = load_data()
            for idx, t in enumerate(data["turnos"]):
                listbox_info.insert(
                    tk.END,
                    f"{idx+1}. {t['paciente']} (DNI: {t.get('dni','N/A')}) | {t['fecha']} | Estado: {t['estado']}",
                )

        cargar_turnos_info()

        def mostrar_detalle_sec(_event):
            try:
                sel = listbox_info.curselection()[0]
                data = load_data()
                t = data["turnos"][sel]
                hist_turno, hist_perfil = self.separar_auditoria_turno_y_perfil(
                    t, data.get("auditoria", []), self.usuario_actual
                )

                turno_txt = (
                    "\n".join(hist_turno)
                    if hist_turno
                    else "   (Sin movimientos registrados para este turno)"
                )
                cuerpo_turno = (
                    f"Paciente: {t['paciente']} | DNI: {t.get('dni', 'N/A')} | Tel: {t.get('contacto', 'N/A')}\n"
                    f"Obra Social: {t['obra_social']} | Afiliado: {t.get('afiliado', 'N/A')}\n"
                    f"Fecha/Hora: {t['fecha']} | Estado: {t['estado']}\n"
                    f"Creado por: {t.get('creado_por', 'N/A')}\n"
                    f"Última modificación: {t.get('modificado_por', 'N/A')} ({t.get('fecha_modificacion', 'N/A')})\n"
                    f"--- Historial del Turno ---\n{turno_txt}\n"
                )
                self.escribir_texto_protegido(txt_detalles_turno, cuerpo_turno)

                perfil_txt = (
                    "\n".join(hist_perfil)
                    if hist_perfil
                    else "   (Sin cambios de perfil o contraseña registrados para esta secretaría)"
                )
                self.escribir_texto_protegido(txt_detalles_perfil, perfil_txt)
            except IndexError:
                pass

        listbox_info.bind("<<ListboxSelect>>", mostrar_detalle_sec)

        frame_nav = tk.Frame(frame_sec)
        frame_nav.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        tk.Button(
            frame_nav,
            text="Cerrar Sesión",
            command=lambda: self.login_view("Secretaria"),
        ).pack(side=tk.LEFT, padx=5)
        self.boton_volver_interfaz(frame_nav).pack(side=tk.LEFT, padx=5)

    # --- INTERFAZ DE MÉDICO / SUPER ADMIN ---
    def doctor_view(self):
        self.clear_window()
        frame_doc = tk.Frame(self.root, padx=12, pady=10)
        frame_doc.grid(row=0, column=0, sticky="nsew")
        frame_doc.columnconfigure(0, weight=1)
        frame_doc.rowconfigure(1, weight=1)

        header = tk.Frame(frame_doc)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        tk.Label(
            header,
            text="Panel Profesional & Super Admin - Dr. Salvador Amado",
            font=("Arial", 13, "bold"),
        ).pack(side=tk.LEFT)
        tk.Button(
            header,
            text="🔑 Cambiar mi Contraseña",
            bg="#0288d1",
            fg="white",
            command=self.abrir_cambio_password,
        ).pack(side=tk.RIGHT)

        notebook = ttk.Notebook(frame_doc)
        notebook.grid(row=1, column=0, sticky="nsew")

        tab_agenda = tk.Frame(notebook, padx=10, pady=10)
        tab_detalle_doc = tk.Frame(notebook, padx=10, pady=10)
        tab_detalle_doc.columnconfigure(0, weight=1)
        tab_detalle_doc.rowconfigure(2, weight=3)
        tab_detalle_doc.rowconfigure(3, weight=2)
        tab_super = tk.Frame(notebook, padx=10, pady=10)
        tab_super.columnconfigure(0, weight=1)
        tab_super.rowconfigure(3, weight=1)

        notebook.add(tab_agenda, text=" 📅 Agenda Médica ")
        notebook.add(tab_detalle_doc, text=" 📋 Historial de Pacientes ")
        notebook.add(tab_super, text=" 🛡️ Super Admin y Auditoría ")

        data = load_data()
        tk.Label(
            tab_agenda,
            text=f"Turnos registrados: {len(data['turnos'])}",
            font=("Arial", 10, "bold"),
            fg="#1565c0",
        ).pack(pady=2)

        lbl_estado_doc = tk.Label(
            tab_agenda, text="", font=("Arial", 9, "bold"), fg="#2e7d32"
        )
        lbl_estado_doc.pack(pady=2)

        listbox_turnos = tk.Listbox(
            tab_agenda, width=115, height=9, exportselection=False
        )
        listbox_turnos.pack(pady=5, fill="x")

        for t in data["turnos"]:
            dni_p = t.get("dni", "N/A")
            visitas_totales = sum(
                1
                for item in data["turnos"]
                if item.get("dni") == dni_p and item.get("estado") == "Atendido"
            )
            req = " (Requiere Reprog.)" if t.get("requiere_nuevo_turno", False) else ""
            listbox_turnos.insert(
                tk.END,
                f"Paciente: {t['paciente']} (DNI: {dni_p} - Visitas atendidas: {visitas_totales}) | Fecha: {t['fecha']} | Estado: {t['estado']}{req}",
            )

        def cambiar_estado(nuevo_estado):
            try:
                idx = listbox_turnos.curselection()[0]
                d = load_data()
                ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                d["turnos"][idx]["estado"] = nuevo_estado
                d["turnos"][idx]["modificado_por"] = "Dr. Amado"
                d["turnos"][idx]["fecha_modificacion"] = ahora_str
                d["auditoria"].append(
                    f"[{ahora_str}] Estado de turno de {d['turnos'][idx]['paciente']} (DNI {d['turnos'][idx].get('dni','N/A')}) cambiado a '{nuevo_estado}' por Dr. Amado"
                )
                save_data(d)
                self.doctor_view()
            except IndexError:
                lbl_estado_doc.config(
                    text="Aviso: Seleccione un turno de la lista.", fg="#ef6c00"
                )

        def marcar_requiere_nuevo():
            try:
                idx = listbox_turnos.curselection()[0]
                d = load_data()
                ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                d["turnos"][idx]["requiere_nuevo_turno"] = True
                d["turnos"][idx]["modificado_por"] = "Dr. Amado"
                d["turnos"][idx]["fecha_modificacion"] = ahora_str
                d["auditoria"].append(
                    f"[{ahora_str}] Dr. Amado indicó reprogramación para {d['turnos'][idx]['paciente']} (DNI {d['turnos'][idx].get('dni','N/A')})"
                )
                save_data(d)
                self.doctor_view()
            except IndexError:
                lbl_estado_doc.config(
                    text="Aviso: Seleccione un turno de la lista.", fg="#ef6c00"
                )

        frame_doc_btn = tk.Frame(tab_agenda)
        frame_doc_btn.pack(pady=6)
        tk.Button(
            frame_doc_btn,
            text="Marcar Atendido",
            bg="green",
            fg="white",
            command=lambda: cambiar_estado("Atendido"),
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            frame_doc_btn,
            text="Marcar Ausente",
            bg="orange",
            fg="white",
            command=lambda: cambiar_estado("Ausente"),
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            frame_doc_btn,
            text="📌 Indicar que requiere nuevo turno",
            bg="#7b1fa2",
            fg="white",
            command=marcar_requiere_nuevo,
        ).pack(side=tk.LEFT, padx=4)

        tk.Label(
            tab_detalle_doc,
            text="Seleccione un turno para consultar su historial y la auditoría del perfil asociado:",
            font=("Arial", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        listbox_det_doc = tk.Listbox(
            tab_detalle_doc, width=115, height=5, exportselection=False
        )
        listbox_det_doc.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        for idx, t in enumerate(data["turnos"]):
            listbox_det_doc.insert(
                tk.END,
                f"{idx+1}. {t['paciente']} (DNI: {t.get('dni','N/A')}) | {t['fecha']} | Estado: {t['estado']}",
            )

        frame_txt_doc = tk.LabelFrame(
            tab_detalle_doc, text=" 🔍 Detalle e Historial del Turno ", padx=8, pady=6
        )
        frame_txt_doc.grid(row=2, column=0, sticky="nsew", pady=(0, 6))
        txt_det_doc = self.crear_caja_texto_desplazable(frame_txt_doc, height=8)

        frame_perfil_doc = tk.LabelFrame(
            tab_detalle_doc,
            text=" 👤 Auditoría de Perfiles Relacionados ",
            padx=8,
            pady=6,
        )
        frame_perfil_doc.grid(row=3, column=0, sticky="nsew")
        txt_perfil_doc = self.crear_caja_texto_desplazable(frame_perfil_doc, height=5)

        def mostrar_detalle_doc(_event):
            try:
                sel = listbox_det_doc.curselection()[0]
                t = data["turnos"][sel]
                mod_txt = str(t.get("modificado_por", ""))
                usuario_ref = ""
                if "(" in mod_txt and ")" in mod_txt:
                    usuario_ref = mod_txt.split("(", 1)[1].split(")", 1)[0].strip()

                hist_turno, hist_perfil = self.separar_auditoria_turno_y_perfil(
                    t, data.get("auditoria", []), usuario_ref
                )

                turno_txt = (
                    "\n".join(hist_turno)
                    if hist_turno
                    else "   (Sin movimientos registrados para este turno)"
                )
                cuerpo = (
                    f"Paciente: {t['paciente']} | DNI: {t.get('dni', 'N/A')} | Tel: {t.get('contacto', 'N/A')}\n"
                    f"Obra Social: {t['obra_social']} | Afiliado: {t.get('afiliado', 'N/A')}\n"
                    f"Fecha/Hora: {t['fecha']} | Estado: {t['estado']}\n"
                    f"Creado por: {t.get('creado_por', 'N/A')}\n"
                    f"Última modificación: {t.get('modificado_por', 'N/A')} ({t.get('fecha_modificacion', 'N/A')})\n"
                    f"--- Historial del Turno ---\n{turno_txt}\n"
                )
                self.escribir_texto_protegido(txt_det_doc, cuerpo)

                perfil_txt = (
                    "\n".join(hist_perfil)
                    if hist_perfil
                    else "   (Sin eventos de perfil o contraseña asociados)"
                )
                self.escribir_texto_protegido(txt_perfil_doc, perfil_txt)
            except IndexError:
                pass

        listbox_det_doc.bind("<<ListboxSelect>>", mostrar_detalle_doc)

        lbl_estado_super = tk.Label(
            tab_super, text="", font=("Arial", 9, "bold"), fg="#2e7d32"
        )
        lbl_estado_super.grid(row=0, column=0, sticky="w", pady=2)

        listbox_users = tk.Listbox(
            tab_super, width=85, height=4, exportselection=False
        )
        listbox_users.grid(row=1, column=0, sticky="ew", pady=4)
        for u in data["usuarios"]:
            listbox_users.insert(
                tk.END,
                f"Usuario: {u['usuario']} | Rol: {u['rol']} | Pass: {u['pass']}",
            )

        frame_alta_usr = tk.Frame(tab_super)
        frame_alta_usr.grid(row=2, column=0, sticky="ew", pady=4)

        tk.Label(frame_alta_usr, text="Nuevo Usuario:").pack(side=tk.LEFT)
        e_new_u = tk.Entry(frame_alta_usr, width=14)
        e_new_u.pack(side=tk.LEFT, padx=4)

        tk.Label(frame_alta_usr, text="Clave:").pack(side=tk.LEFT)
        e_new_p = tk.Entry(frame_alta_usr, width=14)
        e_new_p.pack(side=tk.LEFT, padx=4)

        def registrar_usuario():
            nuevo_u = e_new_u.get().strip()
            nueva_p = e_new_p.get()
            if not nuevo_u or not nueva_p:
                lbl_estado_super.config(
                    text="Error: Complete usuario y contraseña.", fg="#c62828"
                )
                return
            d = load_data()
            if any(u["usuario"] == nuevo_u for u in d["usuarios"]):
                lbl_estado_super.config(
                    text="Error: Ese nombre de usuario ya existe.", fg="#c62828"
                )
                return
            ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            d["usuarios"].append(
                {"usuario": nuevo_u, "pass": nueva_p, "rol": "Secretaria"}
            )
            d["auditoria"].append(
                f"[{ahora_str}] SUPER ADMIN: Creado perfil de secretaria '{nuevo_u}' por Dr. Amado"
            )
            save_data(d)
            self.doctor_view()

        def eliminar_usuario():
            try:
                idx = listbox_users.curselection()[0]
                d = load_data()
                usr = d["usuarios"][idx]
                if usr["rol"] == "Médico":
                    lbl_estado_super.config(
                        text="Error: No se puede eliminar al médico principal.",
                        fg="#c62828",
                    )
                    return
                ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                d["usuarios"].pop(idx)
                d["auditoria"].append(
                    f"[{ahora_str}] SUPER ADMIN: Eliminado perfil de usuario '{usr['usuario']}' por Dr. Amado"
                )
                save_data(d)
                self.doctor_view()
            except IndexError:
                lbl_estado_super.config(
                    text="Aviso: Seleccione un usuario de la lista.", fg="#ef6c00"
                )

        def limpiar_base_datos():
            d = load_data()
            d["turnos"] = []
            d["bloqueos"] = []
            ahora_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            d["auditoria"] = [
                f"[{ahora_str}] SUPER ADMIN: Base de datos limpiada (turnos y registros blanqueados) por Dr. Amado"
            ]
            save_data(d)
            self.doctor_view()

        tk.Button(
            frame_alta_usr,
            text="➕ Agregar Secretaria",
            bg="#0288d1",
            fg="white",
            command=registrar_usuario,
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            frame_alta_usr,
            text="🗑️ Eliminar Seleccionado",
            bg="#d32f2f",
            fg="white",
            command=eliminar_usuario,
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            frame_alta_usr,
            text="⚠️ Limpiar Base de Datos",
            bg="#b71c1c",
            fg="white",
            command=limpiar_base_datos,
        ).pack(side=tk.LEFT, padx=8)

        frame_aud = tk.LabelFrame(
            tab_super, text=" 📜 Registro de Auditoría (Scroll Dual) ", padx=8, pady=6
        )
        frame_aud.grid(row=3, column=0, sticky="nsew", pady=(4, 0))
        txt_aud = self.crear_caja_texto_desplazable(frame_aud, height=7)
        aud_texto = (
            "\n".join(data.get("auditoria", []))
            if data.get("auditoria")
            else "(Sin registros de auditoría)"
        )
        self.escribir_texto_protegido(txt_aud, aud_texto)

        frame_nav = tk.Frame(frame_doc)
        frame_nav.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        tk.Button(
            frame_nav,
            text="Cerrar Sesión",
            command=lambda: self.login_view("Médico"),
        ).pack(side=tk.LEFT, padx=5)
        self.boton_volver_interfaz(frame_nav).pack(side=tk.LEFT, padx=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = ConsultorioApp(root)
    root.mainloop()