import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

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
            ]
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
        self.root.geometry("750x680")
        
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

    # --- MÓDULO PACIENTE ---
    def patient_view(self):
        self.clear_window()
        tk.Label(self.root, text="Portal de Autogestión - Paciente", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self.root, text="Nombre y Apellido del Paciente:").pack()
        e_nombre = tk.Entry(self.root, width=35)
        e_nombre.pack(pady=3)

        tk.Label(self.root, text="DNI / Teléfono de Contacto:").pack()
        e_contacto = tk.Entry(self.root, width=35)
        e_contacto.pack(pady=3)

        tk.Label(self.root, text="Fecha y Hora (Ej: 15/11 - 10:00 hs):").pack()
        e_fecha = tk.Entry(self.root, width=35)
        e_fecha.pack(pady=3)

        tk.Label(self.root, text="Seleccione Cobertura / Obra Social:").pack(pady=3)
        data_init = load_data()
        
        combo_os = ttk.Combobox(self.root, values=data_init["obras_sociales"], width=35, state="readonly")
        combo_os.pack(pady=3)
        combo_os.current(0)

        tk.Label(self.root, text="Número de Afiliado / Credencial (o 'Particular'):").pack(pady=3)
        e_afiliado = tk.Entry(self.root, width=35)
        e_afiliado.pack(pady=3)
        e_afiliado.insert(0, "Sin credencial / Particular")

        def reservar():
            if not e_nombre.get() or not e_contacto.get() or not e_fecha.get() or not e_afiliado.get():
                messagebox.showerror("Error", "Todos los campos obligatorios deben completarse.")
                return
            
            data = load_data()
            for t in data["turnos"]:
                if t["fecha"] == e_fecha.get():
                    messagebox.showwarning("Conflicto", "Ya existe un turno reservado en ese horario exacto.")
                    return

            nuevo_turno = {
                "paciente": e_nombre.get(),
                "contacto": e_contacto.get(),
                "fecha": e_fecha.get(),
                "obra_social": combo_os.get(),
                "afiliado": e_afiliado.get(),
                "estado": "Pendiente"
            }
            data["turnos"].append(nuevo_turno)
            save_data(data)
            messagebox.showinfo("Éxito", "¡Turno reservado correctamente en la agenda central!")
            self.main_menu()

        tk.Button(self.root, text="Confirmar Reserva", bg="green", fg="white", font=("Arial", 10, "bold"), command=reservar).pack(pady=10)
        tk.Button(self.root, text="Volver al Menú Principal", command=self.main_menu).pack(pady=5)

    # --- MÓDULO SECRETARIA ---
    def secretary_view(self):
        self.clear_window()
        tk.Label(self.root, text="Panel Administrativo - Gestión de Agenda Centralizada", font=("Arial", 13, "bold")).pack(pady=15)

        listbox = tk.Listbox(self.root, width=105, height=12)
        listbox.pack(pady=5)

        data = load_data()
        for idx, t in enumerate(data["turnos"]):
            listbox.insert(tk.END, f"{idx+1}. Paciente: {t['paciente']} | Fecha: {t['fecha']} | O.S.: {t['obra_social']} (Afiliado: {t.get('afiliado', 'N/A')}) | Estado: {t['estado']}")

        def cancelar_turno():
            try:
                selected_idx = listbox.curselection()[0]
                data["turnos"].pop(selected_idx)
                save_data(data)
                messagebox.showinfo("Aviso", "Turno cancelado y cupo liberado en la agenda.")
                self.secretary_view()
            except IndexError:
                messagebox.showwarning("Aviso", "Seleccione un turno de la lista para cancelar.")

        tk.Button(self.root, text="Cancelar Turno Seleccionado (Libera Cupo)", bg="#d32f2f", fg="white", font=("Arial", 10, "bold"), command=cancelar_turno).pack(pady=15)
        tk.Button(self.root, text="Cerrar Sesión / Volver al Menú", command=self.main_menu).pack(pady=10)

    # --- MÓDULO MÉDICO / ADMINISTRADOR ---
    def doctor_view(self):
        self.clear_window()
        tk.Label(self.root, text="Panel Profesional y Administración - Dr. Salvador Amado", font=("Arial", 13, "bold")).pack(pady=10)

        data = load_data()
        tk.Label(self.root, text=f"Total de turnos en la jornada: {len(data['turnos'])}", font=("Arial", 10, "bold"), fg="#1565c0").pack(pady=2)
        
        listbox_turnos = tk.Listbox(self.root, width=105, height=6)
        listbox_turnos.pack(pady=5)

        for t in data["turnos"]:
            listbox_turnos.insert(tk.END, f"Paciente: {t['paciente']} | Horario: {t['fecha']} | O.S.: {t['obra_social']} (Afiliado: {t.get('afiliado', 'N/A')}) | Estado: {t['estado']}")

        def cambiar_estado(nuevo_estado):
            try:
                selected_idx = listbox_turnos.curselection()[0]
                data["turnos"][selected_idx]["estado"] = nuevo_estado
                save_data(data)
                messagebox.showinfo("Actualizado", f"Estado cambiado a: {nuevo_estado}")
                self.doctor_view()
            except IndexError:
                messagebox.showwarning("Aviso", "Seleccione un turno de la lista.")

        frame_estados = tk.Frame(self.root)
        frame_estados.pack(pady=2)
        tk.Button(frame_estados, text="Marcar Atendido", bg="green", fg="white", command=lambda: cambiar_estado("Atendido")).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_estados, text="Marcar Ausente", bg="orange", fg="white", command=lambda: cambiar_estado("Ausente")).pack(side=tk.LEFT, padx=5)

        def bloquear_agenda():
            messagebox.showinfo("Bloqueo", "Franja horaria bloqueada por contingencia médica.")

        tk.Button(self.root, text="Bloquear Franja Horaria por Contingencia", bg="#f57c00", fg="white", command=bloquear_agenda).pack(pady=5)

        frame_users = tk.LabelFrame(self.root, text=" Control del Profesional: Gestión de Usuarios / Secretarias ", padx=10, pady=5)
        frame_users.pack(pady=10, fill="x", padx=20)

        listbox_users = tk.Listbox(frame_users, width=50, height=3)
        listbox_users.grid(row=0, column=0, columnspan=4, pady=5, padx=5)

        for idx, u in enumerate(data["usuarios"]):
            listbox_users.insert(tk.END, f"{idx+1}. Usuario: {u['usuario']} | Rol: {u['rol']}")

        tk.Label(frame_users, text="Nuevo Usu:").grid(row=1, column=0, sticky="w")
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
            messagebox.showinfo("Éxito", f"Secretaria/Empleado '{e_new_u.get()}' registrado correctamente.")
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
                messagebox.showinfo("Éxito", f"Usuario '{user_borrado['usuario']}' eliminado del sistema.")
                self.doctor_view()
            except IndexError:
                messagebox.showwarning("Aviso", "Seleccione un usuario de la lista para eliminar.")

        tk.Button(frame_users, text="➕ Agregar Secretaria", bg="#0288d1", fg="white", command=registrar_usuario).grid(row=1, column=4, padx=5)
        tk.Button(frame_users, text="🗑️ Quitar Usuario", bg="#d32f2f", fg="white", command=eliminar_usuario).grid(row=0, column=4, padx=5)

        tk.Button(self.root, text="Cerrar Sesión / Volver al Menú", command=self.main_menu).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConsultorioApp(root)
    root.mainloop()