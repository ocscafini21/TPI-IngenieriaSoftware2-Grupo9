import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

DATA_FILE = "database.json"

def init_db():
    if not os.path.exists(DATA_FILE):
        data = {
            "turnos": [],
            "usuarios": [
                {"usuario": "admin", "pass": "1234", "rol": "Secretaria"},
                {"usuario": "amado", "pass": "medico2026", "rol": "Médico"}
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
                "Accord Salud"
            ],
            "bloqueos": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

class ConsultorioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión - Consultorio Dr. Salvador Amado")
        self.root.geometry("820x720")
        
        init_db()
        self.main_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_window()
        
        tk.Label(self.root, text="Clínica Médica - Dr. Salvador Amado", font=("Arial", 16, "bold")).pack(pady=20)
        tk.Label(self.root, text="Seleccione el módulo de acceso:", font=("Arial", 11, "italic")).pack(pady=5)

        tk.Button(self.root, text="👤 Módulo Paciente (Autogestión de Turnos)", width=42, height=2, bg="#e1f5fe", command=self.patient_view).pack(pady=10)
        tk.Button(self.root, text="👩‍💼 Panel Administrativo / Secretaria (Login)", width=42, height=2, bg="#e8f5e9", command=lambda: self.login_view("Secretaria")).pack(pady=10)
        tk.Button(self.root, text="🩺 Panel Médico / Administrador - Dr. Amado (Login)", width=42, height=2, bg="#fff3e0", command=lambda: self.login_view("Médico")).pack(pady=10)
        tk.Button(self.root, text="❌ Salir del Sistema", width=25, command=self.root.quit).pack(pady=20)

    # --- LOGIN SIMULADO ---
    def login_view(self, rol_requerido):
        self.clear_window()
        tk.Label(self.root, text=f"Acceso Restringido - {rol_requerido}", font=("Arial", 14, "bold")).pack(pady=20)

        tk.Label(self.root, text="Usuario:").pack()
        e_user = tk.Entry(self.root, width=30)
        e_user.pack(pady=5)

        tk.Label(self.root, text="Contraseña:").pack()
        e_pass = tk.Entry(self.root, width=30, show="*")
        e_pass.pack(pady=5)

        def validar_ingreso():
            data = load_data()
            usuario_ingresado = e_user.get()
            pass_ingresada = e_pass.get()

            for u in data["usuarios"]:
                if u["usuario"] == usuario_ingresado and u["pass"] == pass_ingresada and u["rol"] == rol_requerido:
                    messagebox.showinfo("Éxito", f"Bienvenido/a, {usuario_ingresado}")
                    if rol_requerido == "Secretaria":
                        self.secretary_view()
                    else:
                        self.doctor_view()
                    return
            messagebox.showerror("Error de Autenticación", "Usuario, contraseña o rol incorrectos.")

        tk.Button(self.root, text="Ingresar", bg="green", fg="white", width=20, command=validar_ingreso).pack(pady=15)
        tk.Button(self.root, text="Volver al Menú Principal", command=self.main_menu).pack()

    # --- SELECTOR DE HORARIOS Y DISPONIBILIDAD (30 min - Lunes a Viernes 8 a 16 hs) ---
    def abrir_selector_horario(self, callback_asignar):
        ventana_sel = tk.Toplevel(self.root)
        ventana_sel.title("Selector de Disponibilidad - Agenda")
        ventana_sel.geometry("450x400")

        tk.Label(ventana_sel, text="Seleccione Fecha (DD/MM/AAAA):", font=("Arial", 10, "bold")).pack(pady=5)
        e_fecha_sel = tk.Entry(ventana_sel, width=20)
        e_fecha_sel.pack(pady=3)
        e_fecha_sel.insert(0, datetime.now().strftime("%d/%m/%Y"))

        tk.Label(ventana_sel, text="Horarios Disponibles (Intervalos de 30 min, Lun-Vie 8 a 16hs):", font=("Arial", 9, "italic")).pack(pady=5)
        
        # Generar grilla de horarios de 8:00 a 15:30 (último turno antes de las 16)
        horarios_base = []
        for h in range(8, 16):
            horarios_base.append(f"{h:02d}:00")
            if h < 16:
                horarios_base.append(f"{h:02d}:30")

        listbox_horas = tk.Listbox(ventana_sel, width=25, height=10)
        listbox_horas.pack(pady=5)

        for hora in horarios_base:
            listbox_horas.insert(tk.END, hora)

        def confirmar_seleccion():
            fecha = e_fecha_sel.get()
            try:
                # Validar formato de fecha
                dt = datetime.strptime(fecha, "%d/%m/%Y")
                # Validar Lunes a Viernes (0=Lunes, 4=Viernes)
                if dt.weekday() > 4:
                    messagebox.showerror("Error", "El consultorio solo atiende de Lunes a Viernes.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/AAAA.")
                return

            try:
                selected_idx = listbox_horas.curselection()[0]
                hora_elegida = listbox_horas.get(selected_idx)
            except IndexError:
                messagebox.showwarning("Aviso", "Seleccione un horario de la lista.")
                return

            # Validar que no exista turno en esa franja exacta (respetando 30 min)
            data = load_data()
            fecha_hora_completa = f"{fecha} - {hora_elegida} hs"
            
            for t in data["turnos"]:
                if t["fecha"] == fecha_hora_completa:
                    messagebox.showwarning("Conflicto", "Este horario ya se encuentra ocupado por otro paciente.")
                    return

            callback_asignar(fecha_hora_completa)
            ventana_sel.destroy()

        tk.Button(ventana_sel, text="Confirmar Horario", bg="green", fg="white", command=confirmar_seleccion).pack(pady=10)

    # --- MÓDULO PACIENTE ---
    def patient_view(self):
        self.clear_window()
        tk.Label(self.root, text="Portal de Autogestión - Paciente", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self.root, text="Nombre y Apellido:").pack()
        e_nombre = tk.Entry(self.root, width=35)
        e_nombre.pack(pady=2)

        tk.Label(self.root, text="DNI:").pack()
        e_dni = tk.Entry(self.root, width=35)
        e_dni.pack(pady=2)

        tk.Label(self.root, text="Teléfono de Contacto:").pack()
        e_contacto = tk.Entry(self.root, width=35)
        e_contacto.pack(pady=2)

        tk.Label(self.root, text="Seleccione Cobertura / Obra Social:").pack(pady=3)
        data_init = load_data()
        combo_os = ttk.Combobox(self.root, values=data_init["obras_sociales"], width=33, state="readonly")
        combo_os.pack(pady=2)
        combo_os.current(0)

        tk.Label(self.root, text="Número de Afiliado / Credencial:").pack(pady=3)
        e_afiliado = tk.Entry(self.root, width=35)
        e_afiliado.pack(pady=2)
        e_afiliado.insert(0, "Particular / Sin credencial")

        lbl_turno_elegido = tk.Label(self.root, text="Turno seleccionado: [Ninguno]", font=("Arial", 10, "bold"), fg="#1565c0")
        lbl_turno_elegido.pack(pady=8)

        selected_slot = {"val": ""}

        def seleccionar_horario():
            def asignar(fh):
                selected_slot["val"] = fh
                lbl_turno_elegido.config(text=f"Turno seleccionado: {fh}")
            self.abrir_selector_horario(asignar)

        tk.Button(self.root, text="📅 Ver Calendario y Elegir Horario", bg="#0288d1", fg="white", command=seleccionar_horario).pack(pady=5)

        def reservar():
            if not e_nombre.get() or not e_dni.get() or not e_contacto.get() or not selected_slot["val"]:
                messagebox.showerror("Error", "Complete todos los datos personales y seleccione un horario válido.")
                return
            
            data = load_data()
            nuevo_turno = {
                "paciente": e_nombre.get(),
                "dni": e_dni.get(),
                "contacto": e_contacto.get(),
                "fecha": selected_slot["val"],
                "obra_social": combo_os.get(),
                "afiliado": e_afiliado.get(),
                "estado": "Pendiente",
                "requiere_nuevo_turno": False
            }
            data["turnos"].append(nuevo_turno)
            save_data(data)
            messagebox.showinfo("Éxito", "¡Turno reservado correctamente!")
            self.main_menu()

        tk.Button(self.root, text="Confirmar Reserva", bg="green", fg="white", font=("Arial", 10, "bold"), command=reservar).pack(pady=10)
        tk.Button(self.root, text="Volver al Menú Principal", command=self.main_menu).pack(pady=5)

    # --- MÓDULO SECRETARIA ---
    def secretary_view(self):
        self.clear_window()
        tk.Label(self.root, text="Panel Administrativo - Gestión de Agenda", font=("Arial", 13, "bold")).pack(pady=10)

        # Alertas de pacientes que requieren nuevo turno por indicación del médico
        data = load_data()
        pendientes_reprog = [t for t in data["turnos"] if t.get("requiere_nuevo_turno", False)]
        if pendientes_reprog:
            lbl_aviso = tk.Label(self.root, text=f"⚠️ Hay {len(pendientes_reprog)} paciente(s) marcados por el Dr. para reasignar turno.", fg="red", font=("Arial", 9, "bold"))
            lbl_aviso.pack(pady=2)

        listbox = tk.Listbox(self.root, width=115, height=12)
        listbox.pack(pady=5)

        for idx, t in enumerate(data["turnos"]):
            alerta_txt = " [¡REQUIERE NUEVO TURNO!]" if t.get("requiere_nuevo_turno", False) else ""
            listbox.insert(tk.END, f"{idx+1}. Paciente: {t['paciente']} (DNI: {t.get('dni','N/A')}) | Fecha: {t['fecha']} | O.S.: {t['obra_social']} | Estado: {t['estado']}{alerta_txt}")

        def cancelar_turno():
            try:
                selected_idx = listbox.curselection()[0]
                data["turnos"].pop(selected_idx)
                save_data(data)
                messagebox.showinfo("Aviso", "Turno cancelado y cupo liberado.")
                self.secretary_view()
            except IndexError:
                messagebox.showwarning("Aviso", "Seleccione un turno de la lista.")

        def reprogramar_turno():
            try:
                selected_idx = listbox.curselection()[0]
                turno_obj = data["turnos"][selected_idx]

                def asignar_nuevo(nueva_fecha):
                    data_reprog = load_data()
                    data_reprog["turnos"][selected_idx]["fecha"] = nueva_fecha
                    data_reprog["turnos"][selected_idx]["estado"] = "Pendiente"
                    data_reprog["turnos"][selected_idx]["requiere_nuevo_turno"] = False # Limpiar alerta
                    save_data(data_reprog)
                    messagebox.showinfo("Éxito", f"Turno reprogramado con éxito para: {nueva_fecha}")
                    self.secretary_view()

                self.abrir_selector_horario(asignar_nuevo)
            except IndexError:
                messagebox.showwarning("Aviso", "Seleccione un turno de la lista para reprogramar.")

        frame_sec_botones = tk.Frame(self.root)
        frame_sec_botones.pack(pady=10)
        tk.Button(frame_sec_botones, text="🔄 Reprogramar Turno (Calendario)", bg="#0288d1", fg="white", font=("Arial", 10, "bold"), command=reprogramar_turno).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_sec_botones, text="❌ Cancelar Turno", bg="#d32f2f", fg="white", font=("Arial", 10, "bold"), command=cancelar_turno).pack(side=tk.LEFT, padx=5)

        tk.Button(self.root, text="Cerrar Sesión / Volver al Menú", command=self.main_menu).pack(pady=5)

    # --- MÓDULO MÉDICO / ADMINISTRADOR ---
    def doctor_view(self):
        self.clear_window()
        tk.Label(self.root, text="Panel Profesional - Dr. Salvador Amado", font=("Arial", 13, "bold")).pack(pady=10)

        data = load_data()
        tk.Label(self.root, text=f"Turnos en agenda: {len(data['turnos'])} | Bloqueos activos: {len(data.get('bloqueos',[]))}", font=("Arial", 9, "bold"), fg="#1565c0").pack(pady=2)
        
        listbox_turnos = tk.Listbox(self.root, width=115, height=6)
        listbox_turnos.pack(pady=5)

        for t in data["turnos"]:
            req = " (Solicita reasignación)" if t.get("requiere_nuevo_turno", False) else ""
            listbox_turnos.insert(tk.END, f"Paciente: {t['paciente']} | Horario: {t['fecha']} | O.S.: {t['obra_social']} | Estado: {t['estado']}{req}")

        def cambiar_estado(nuevo_estado):
            try:
                selected_idx = listbox_turnos.curselection()[0]
                data["turnos"][selected_idx]["estado"] = nuevo_estado
                save_data(data)
                messagebox.showinfo("Actualizado", f"Estado cambiado a: {nuevo_estado}")
                self.doctor_view()
            except IndexError:
                messagebox.showwarning("Aviso", "Seleccione un turno de la lista.")

        def marcar_requiere_nuevo():
            try:
                selected_idx = listbox_turnos.curselection()[0]
                data["turnos"][selected_idx]["requiere_nuevo_turno"] = True
                save_data(data)
                messagebox.showinfo("Indicación Guardada", "Se indicó que este paciente necesita un nuevo turno. La secretaría lo verá en su panel.")
                self.doctor_view()
            except IndexError:
                messagebox.showwarning("Aviso", "Seleccione un turno de la lista.")

        frame_doc_est = tk.Frame(self.root)
        frame_doc_est.pack(pady=3)
        tk.Button(frame_doc_est, text="Marcar Atendido", bg="green", fg="white", command=lambda: cambiar_estado("Atendido")).pack(side=tk.LEFT, padx=3)
        tk.Button(frame_doc_est, text="Marcar Ausente", bg="orange", fg="white", command=lambda: cambiar_estado("Ausente")).pack(side=tk.LEFT, padx=3)
        tk.Button(frame_doc_est, text="📌 Indicar que requiere nuevo turno", bg="#7b1fa2", fg="white", command=marcar_requiere_nuevo).pack(side=tk.LEFT, padx=3)

        def bloquear_franja():
            def registrar_bloqueo(fecha_hora):
                d = load_data()
                if "bloqueos" not in d:
                    d["bloqueos"] = []
                d["bloqueos"].append(fecha_hora)
                save_data(d)
                messagebox.showinfo("Bloqueo Exitoso", f"Franja horaria bloqueada por contingencia: {fecha_hora}")
            self.abrir_selector_horario(registrar_bloqueo)

        tk.Button(self.root, text="🔒 Bloquear Franja Horaria (Usando Calendario)", bg="#f57c00", fg="white", command=bloquear_franja).pack(pady=5)

        # Gestión de Secretarias (Usuarios)
        frame_users = tk.LabelFrame(self.root, text=" Gestión de Secretarias / Personal ", padx=10, pady=5)
        frame_users.pack(pady=5, fill="x", padx=20)

        listbox_users = tk.Listbox(frame_users, width=50, height=3)
        listbox_users.grid(row=0, column=0, columnspan=4, pady=3, padx=5)

        for idx, u in enumerate(data["usuarios"]):
            listbox_users.insert(tk.END, f"{idx+1}. Usuario: {u['usuario']} | Rol: {u['rol']}")

        tk.Label(frame_users, text="Usuario:").grid(row=1, column=0, sticky="w")
        e_new_u = tk.Entry(frame_users, width=12)
        e_new_u.grid(row=1, column=1, padx=2)

        tk.Label(frame_users, text="Clave:").grid(row=1, column=2, sticky="w")
        e_new_p = tk.Entry(frame_users, width=12, show="*")
        e_new_p.grid(row=1, column=3, padx=2)

        def registrar_usuario():
            if not e_new_u.get() or not e_new_p.get():
                messagebox.showerror("Error", "Complete usuario y contraseña.")
                return
            d = load_data()
            d["usuarios"].append({"usuario": e_new_u.get(), "pass": e_new_p.get(), "rol": "Secretaria"})
            save_data(d)
            messagebox.showinfo("Éxito", f"Secretaria '{e_new_u.get()}' registrada.")
            self.doctor_view()

        def eliminar_usuario():
            try:
                selected_idx = listbox_users.curselection()[0]
                d = load_data()
                user_borrado = d["usuarios"][selected_idx]
                if user_borrado["rol"] == "Médico":
                    messagebox.showerror("Error", "No se puede eliminar la cuenta principal del Doctor.")
                    return
                d["usuarios"].pop(selected_idx)
                save_data(d)
                messagebox.showinfo("Éxito", f"Usuario '{user_borrado['usuario']}' eliminado.")
                self.doctor_view()
            except IndexError:
                messagebox.showwarning("Aviso", "Seleccione un usuario de la lista.")

        tk.Button(frame_users, text="➕ Agregar", bg="#0288d1", fg="white", command=registrar_usuario).grid(row=1, column=4, padx=5)
        tk.Button(frame_users, text="🗑️ Quitar", bg="#d32f2f", fg="white", command=eliminar_usuario).grid(row=0, column=4, padx=5)

        tk.Button(self.root, text="Cerrar Sesión / Volver al Menú", command=self.main_menu).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConsultorioApp(root)
    root.mainloop()