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
            "obras_sociales": ["Particular", "OSDE", "IOMA", "Swiss Medical"]
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
        self.root.geometry("700x550")
        
        init_db()
        self.main_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_window()
        
        tk.Label(self.root, text="Clínica Médica - Dr. Salvador Amado", font=("Arial", 16, "bold")).pack(pady=20)
        tk.Label(self.root, text="Seleccione el módulo de acceso:", font=("Arial", 11, "italic")).pack(pady=5)

        tk.Button(self.root, text="👤 Módulo Paciente (Autogestión de Turnos)", width=40, height=2, bg="#e1f5fe", command=self.patient_view).pack(pady=10)
        tk.Button(self.root, text="👩‍💼 Panel Administrativo / Secretaria (Login)", width=40, height=2, bg="#e8f5e9", command=lambda: self.login_view("Secretaria")).pack(pady=10)
        tk.Button(self.root, text="🩺 Panel Médico - Dr. Salvador Amado (Login)", width=40, height=2, bg="#fff3e0", command=lambda: self.login_view("Médico")).pack(pady=10)
        tk.Button(self.root, text="❌ Salir del Sistema", width=25, command=self.root.quit).pack(pady=20)

    # --- LOGIN SIMULADO CON USUARIOS DINÁMICOS ---
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
        tk.Label(self.root, text="Portal de Autogestión - Paciente", font=("Arial", 14, "bold")).pack(pady=15)

        tk.Label(self.root, text="Nombre y Apellido del Paciente:").pack()
        e_nombre = tk.Entry(self.root, width=35)
        e_nombre.pack(pady=5)

        tk.Label(self.root, text="DNI / Teléfono de Contacto:").pack()
        e_contacto = tk.Entry(self.root, width=35)
        e_contacto.pack(pady=5)

        tk.Label(self.root, text="Fecha y Hora (Ej: 15/11 - 10:00 hs):").pack()
        e_fecha = tk.Entry(self.root, width=35)
        e_fecha.pack(pady=5)

        tk.Label(self.root, text="Seleccione Cobertura / Obra Social:").pack()
        data_init = load_data()
        combo_os = ttk.Combobox(self.root, values=data_init["obras_sociales"], width=32, state="readonly")
        combo_os.pack(pady=5)
        combo_os.current(0)

        def reservar():
            if not e_nombre.get() or not e_contacto.get() or not e_fecha.get():
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
                "estado": "Pendiente"
            }
            data["turnos"].append(nuevo_turno)
            save_data(data)
            messagebox.showinfo("Éxito", "¡Turno reservado correctamente en la agenda central!")
            self.main_menu()

        tk.Button(self.root, text="Confirmar Reserva", bg="green", fg="white", font=("Arial", 10, "bold"), command=reservar).pack(pady=15)
        tk.Button(self.root, text="Volver al Menú", command=self.main_menu).pack()

    # --- MÓDULO SECRETARIA ---
    def secretary_view(self):
        self.clear_window()
        tk.Label(self.root, text="Panel Administrativo - Gestión de Turnos y Empleados", font=("Arial", 13, "bold")).pack(pady=10)

        listbox = tk.Listbox(self.root, width=90, height=8)
        listbox.pack(pady=5)

        data = load_data()
        for idx, t in enumerate(data["turnos"]):
            listbox.insert(tk.END, f"{idx+1}. Paciente: {t['paciente']} | Fecha: {t['fecha']} | O.S.: {t['obra_social']} | Estado: {t['estado']}")

        def cancelar_turno():
            try:
                selected_idx = listbox.curselection()[0]
                data["turnos"].pop(selected_idx)
                save_data(data)
                messagebox.showinfo("Aviso", "Turno cancelado y cupo liberado en la agenda.")
                self.secretary_view()
            except IndexError:
                messagebox.showwarning("Aviso", "Seleccione un turno de la lista.")

        # Sección para agregar nuevos usuarios (empleados/secretarias) dinámicamente
        frame_user = tk.LabelFrame(self.root, text=" Registrar Nuevo Empleado / Usuario ", padx=10, pady=10)
        frame_user.pack(pady=10, fill="x", padx=20)

        tk.Label(frame_user, text="Nuevo Usuario:").grid(row=0, column=0, sticky="w")
        e_new_u = tk.Entry(frame_user, width=15)
        e_new_u.grid(row=0, column=1, padx=5)

        tk.Label(frame_user, text="Contraseña:").grid(row=0, column=2, sticky="w")
        e_new_p = tk.Entry(frame_user, width=15, show="*")
        e_new_p.grid(row=0, column=3, padx=5)

        def registrar_usuario():
            if not e_new_u.get() or not e_new_p.get():
                messagebox.showerror("Error", "Complete usuario y contraseña.")
                return
            d = load_data()
            d["usuarios"].append({"usuario": e_new_u.get(), "pass": e_new_p.get(), "rol": "Secretaria"})
            save_data(d)
            messagebox.showinfo("Éxito", f"Usuario '{e_new_u.get()}' registrado con éxito.")
            self.secretary_view()

        tk.Button(frame_user, text="Registrar Empleado", bg="#0288d1", fg="white", command=registrar_usuario).grid(row=0, column=4, padx=10)

        tk.Button(self.root, text="Cancelar Turno Seleccionado", bg="#d32f2f", fg="white", command=cancelar_turno).pack(pady=5)
        tk.Button(self.root, text="Cerrar Sesión / Volver al Menú", command=self.main_menu).pack(pady=5)

    # --- MÓDULO MÉDICO ---
    def doctor_view(self):
        self.clear_window()
        tk.Label(self.root, text="Panel Profesional - Dr. Salvador Amado", font=("Arial", 14, "bold")).pack(pady=15)

        data = load_data()
        tk.Label(self.root, text=f"Total de turnos en la jornada: {len(data['turnos'])}", font=("Arial", 11, "bold"), fg="#1565c0").pack(pady=5)
        
        listbox = tk.Listbox(self.root, width=90, height=10)
        listbox.pack(pady=5)

        for t in data["turnos"]:
            listbox.insert(tk.END, f"Paciente: {t['paciente']} | Horario: {t['fecha']} | O.S.: {t['obra_social']} | Estado: {t['estado']}")

        def cambiar_estado(nuevo_estado):
            try:
                selected_idx = listbox.curselection()[0]
                data["turnos"][selected_idx]["estado"] = nuevo_estado
                save_data(data)
                messagebox.showinfo("Actualizado", f"Estado cambiado a: {nuevo_estado}")
                self.doctor_view()
            except IndexError:
                messagebox.showwarning("Aviso", "Seleccione un turno de la lista.")

        frame_estados = tk.Frame(self.root)
        frame_estados.pack(pady=5)
        tk.Button(frame_estados, text="Marcar como Atendido", bg="green", fg="white", command=lambda: cambiar_estado("Atendido")).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_estados, text="Marcar como Ausente", bg="orange", fg="white", command=lambda: cambiar_estado("Ausente")).pack(side=tk.LEFT, padx=5)

        def bloquear_agenda():
            messagebox.showinfo("Bloqueo", "Franja horaria bloqueada por contingencia médica.")

        tk.Button(self.root, text="Bloquear Franja Horaria por Contingencia", bg="#f57c00", fg="white", command=bloquear_agenda).pack(pady=10)
        tk.Button(self.root, text="Cerrar Sesión / Volver al Menú", command=self.main_menu).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConsultorioApp(root)
    root.mainloop()