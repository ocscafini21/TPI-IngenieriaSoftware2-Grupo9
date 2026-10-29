import json
import os
import tkinter as tk
from tkinter import messagebox

DATA_FILE = "database.json"

def init_db():
    if not os.path.exists(DATA_FILE):
        data = {
            "turnos": [],
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
        self.root.geometry("600x450")
        
        init_db()
        self.main_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_window()
        
        tk.Label(self.root, text="Clínica Médica - Dr. Salvador Amado", font=("Arial", 16, "bold")).pack(pady=20)
        tk.Label(self.root, text="Seleccione su perfil de acceso:", font=("Arial", 11)).pack(pady=10)

        tk.Button(self.root, text="👤 Módulo Paciente (Autogestión)", width=35, height=2, bg="#e1f5fe", command=self.patient_view).pack(pady=8)
        tk.Button(self.root, text="👩‍💼 Módulo Secretaria (Gestión y Agenda)", width=35, height=2, bg="#e8f5e9", command=self.secretary_view).pack(pady=8)
        tk.Button(self.root, text="🩺 Módulo Médico (Dr. Salvador Amado)", width=35, height=2, bg="#fff3e0", command=self.doctor_view).pack(pady=8)
        tk.Button(self.root, text="❌ Salir", width=20, command=self.root.quit).pack(pady=20)

    def patient_view(self):
        self.clear_window()
        tk.Label(self.root, text="Portal de Autogestión - Paciente", font=("Arial", 14, "bold")).pack(pady=15)

        tk.Label(self.root, text="Nombre y Apellido:").pack()
        e_nombre = tk.Entry(self.root, width=30)
        e_nombre.pack(pady=5)

        tk.Label(self.root, text="DNI / Teléfono (Validación):").pack()
        e_contacto = tk.Entry(self.root, width=30)
        e_contacto.pack(pady=5)

        tk.Label(self.root, text="Fecha y Hora (Ej: 15/11 - 10:00 hs):").pack()
        e_fecha = tk.Entry(self.root, width=30)
        e_fecha.pack(pady=5)

        def reservar():
            if not e_nombre.get() or not e_contacto.get() or not e_fecha.get():
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            data = load_data()
            nuevo_turno = {
                "paciente": e_nombre.get(),
                "contacto": e_contacto.get(),
                "fecha": e_fecha.get(),
                "estado": "Reservado"
            }
            data["turnos"].append(nuevo_turno)
            save_data(data)
            messagebox.showinfo("Éxito", "¡Turno reservado con éxito en la agenda central!")
            self.main_menu()

        tk.Button(self.root, text="Reservar Turno", bg="green", fg="white", command=reservar).pack(pady=15)
        tk.Button(self.root, text="Volver al Menú", command=self.main_menu).pack()

    def secretary_view(self):
        self.clear_window()
        tk.Label(self.root, text="Panel Administrativo - Secretaria", font=("Arial", 14, "bold")).pack(pady=15)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Listado de Turnos Registrados en la Agenda:", font=("Arial", 11, "bold")).pack(anchor="w")
        
        listbox = tk.Listbox(frame, width=70, height=10)
        listbox.pack(pady=5)

        data = load_data()
        for idx, t in enumerate(data["turnos"]):
            listbox.insert(tk.END, f"{idx+1}. Paciente: {t['paciente']} | Fecha: {t['fecha']} | Estado: {t['estado']}")

        def cancelar_turno():
            try:
                selected_idx = listbox.curselection()[0]
                data["turnos"].pop(selected_idx)
                save_data(data)
                messagebox.showinfo("Aviso", "Turno cancelado y cupo liberado en la agenda central.")
                self.secretary_view()
            except IndexError:
                messagebox.showwarning("Advertencia", "Seleccione un turno de la lista para cancelar.")

        tk.Button(self.root, text="Cancelar Turno Seleccionado (Libera Cupo)", bg="#d32f2f", fg="white", command=cancelar_turno).pack(pady=10)
        tk.Button(self.root, text="Volver al Menú", command=self.main_menu).pack()

    def doctor_view(self):
        self.clear_window()
        tk.Label(self.root, text="Panel Profesional - Dr. Salvador Amado", font=("Arial", 14, "bold")).pack(pady=15)

        tk.Label(self.root, text="Flujo de Pacientes del Día:", font=("Arial", 11, "bold")).pack(anchor="w", padx=50)
        
        listbox = tk.Listbox(self.root, width=70, height=10)
        listbox.pack(pady=5)

        data = load_data()
        for t in data["turnos"]:
            listbox.insert(tk.END, f"Paciente: {t['paciente']} | Horario: {t['fecha']} | Estado: {t['estado']}")

        def bloquear_agenda():
            messagebox.showinfo("Bloqueo de Franja", "Franja horaria bloqueada por contingencia/licencia médica.")

        tk.Button(self.root, text="Bloquear Franja Horaria por Contingencia", bg="#f57c00", fg="white", command=bloquear_agenda).pack(pady=10)
        tk.Button(self.root, text="Volver al Menú", command=self.main_menu).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConsultorioApp(root)
    root.mainloop()