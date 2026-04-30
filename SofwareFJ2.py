"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Con Interfaz Gráfica Profesional (Tkinter)
Curso: Programación - Código: 213023
Universidad Nacional Abierta y a Distancia
"""

import datetime
import logging
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from abc import ABC, abstractmethod
from typing import List, Optional
from PIL import Image, ImageTk  # Necesitas instalar: pip install Pillow

# ========================= CONFIGURACIÓN DE LOGS =========================
LOG_FILE = "sistema_logs.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
    ]
)

# ======================== EXCEPCIONES PERSONALIZADAS ========================
class SistemaError(Exception):
    pass

class ClienteInvalidoError(SistemaError):
    pass

class ServicioNoDisponibleError(SistemaError):
    pass

class ReservaInvalidaError(SistemaError):
    pass

class ParametroFaltanteError(SistemaError):
    pass

# ========================= CLASE ABSTRACTA ENTIDAD =========================
class Entidad(ABC):
    def __init__(self, id_entidad: str, nombre: str):
        self._id_entidad = id_entidad
        self._nombre = nombre
    
    @abstractmethod
    def obtener_descripcion(self) -> str:
        pass
    
    def get_id(self) -> str:
        return self._id_entidad
    
    def get_nombre(self) -> str:
        return self._nombre
    
    def set_nombre(self, nombre: str) -> None:
        if not nombre or len(nombre.strip()) == 0:
            raise ClienteInvalidoError("El nombre no puede estar vacío")
        self._nombre = nombre

# ========================= CLASE CLIENTE =========================
class Cliente(Entidad):
    def __init__(self, id_cliente: str, nombre: str, email: str, telefono: str):
        super().__init__(id_cliente, nombre)
        self._email = None
        self._telefono = None
        self.set_email(email)
        self.set_telefono(telefono)
        logging.info(f"Cliente creado: {nombre} (ID: {id_cliente})")
    
    def set_email(self, email: str) -> None:
        if not email or "@" not in email or "." not in email:
            raise ClienteInvalidoError(f"Email inválido: {email}")
        self._email = email
    
    def set_telefono(self, telefono: str) -> None:
        if not telefono or len(telefono.strip()) < 7:
            raise ClienteInvalidoError(f"Teléfono inválido: {telefono}")
        self._telefono = telefono
    
    def get_email(self) -> str:
        return self._email
    
    def get_telefono(self) -> str:
        return self._telefono
    
    def obtener_descripcion(self) -> str:
        return f"{self._nombre} | {self._email} | {self._telefono}"
    
    def __str__(self) -> str:
        return self.obtener_descripcion()

# ========================= CLASE ABSTRACTA SERVICIO =========================
class Servicio(Entidad, ABC):
    def __init__(self, id_servicio: str, nombre: str, precio_base: float):
        super().__init__(id_servicio, nombre)
        if precio_base < 0:
            raise ServicioNoDisponibleError("El precio base no puede ser negativo")
        self._precio_base = precio_base
    
    @abstractmethod
    def calcular_costo(self, duracion_horas: float = 1, **kwargs) -> float:
        pass
    
    @abstractmethod
    def validar_parametros(self, **kwargs) -> bool:
        pass
    
    def get_precio_base(self) -> float:
        return self._precio_base

# ========================= SERVICIOS ESPECIALIZADOS =========================
class ReservaSalas(Servicio):
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, capacidad_maxima: int):
        super().__init__(id_servicio, nombre, precio_base)
        self._capacidad_maxima = capacidad_maxima
    
    def calcular_costo(self, duracion_horas: float = 1, **kwargs) -> float:
        costo = self._precio_base * duracion_horas
        descuento = kwargs.get('descuento', 0.0)
        if descuento < 0 or descuento > 100:
            raise ParametroFaltanteError(f"Descuento inválido: {descuento}")
        costo = costo * (1 - descuento / 100)
        aplicar_impuesto = kwargs.get('aplicar_impuesto', False)
        if aplicar_impuesto:
            costo = costo * 1.19
        return round(costo, 2)
    
    def validar_parametros(self, **kwargs) -> bool:
        duracion = kwargs.get('duracion_horas', 0)
        if duracion <= 0:
            raise ServicioNoDisponibleError("La duración debe ser mayor a 0 horas")
        if duracion > 24:
            raise ServicioNoDisponibleError("La duración no puede exceder 24 horas")
        return True
    
    def obtener_descripcion(self) -> str:
        return f"🏛️ Sala: {self._nombre} (Cap: {self._capacidad_maxima})"

class AlquilerEquipos(Servicio):
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, tipo_equipo: str):
        super().__init__(id_servicio, nombre, precio_base)
        self._tipo_equipo = tipo_equipo
    
    def calcular_costo(self, duracion_horas: float = 1, **kwargs) -> float:
        cantidad = kwargs.get('cantidad', 1)
        if cantidad <= 0:
            raise ParametroFaltanteError("La cantidad debe ser mayor a 0")
        costo = self._precio_base * duracion_horas * cantidad
        if cantidad >= 5:
            costo = costo * 0.90
        return round(costo, 2)
    
    def validar_parametros(self, **kwargs) -> bool:
        cantidad = kwargs.get('cantidad', 0)
        if cantidad <= 0:
            raise ServicioNoDisponibleError("La cantidad de equipos debe ser mayor a 0")
        if cantidad > 50:
            raise ServicioNoDisponibleError("No se pueden alquilar más de 50 equipos")
        return True
    
    def obtener_descripcion(self) -> str:
        return f"💻 Equipo: {self._nombre} ({self._tipo_equipo})"

class AsesoriasEspecializadas(Servicio):
    def __init__(self, id_servicio: str, nombre: str, precio_base: float, especialidad: str):
        super().__init__(id_servicio, nombre, precio_base)
        self._especialidad = especialidad
    
    def calcular_costo(self, duracion_horas: float = 1, **kwargs) -> float:
        costo = self._precio_base * duracion_horas
        es_frecuente = kwargs.get('es_frecuente', False)
        if es_frecuente:
            costo = costo * 0.85
        return round(costo, 2)
    
    def validar_parametros(self, **kwargs) -> bool:
        duracion = kwargs.get('duracion_horas', 0)
        if duracion <= 0:
            raise ServicioNoDisponibleError("La duración debe ser mayor a 0 horas")
        if duracion > 8:
            raise ServicioNoDisponibleError("Una asesoría no puede durar más de 8 horas")
        return True
    
    def obtener_descripcion(self) -> str:
        return f"🎓 Asesoría: {self._nombre} ({self._especialidad})"

# ========================= CLASE RESERVA =========================
class Reserva:
    _contador_reservas = 0
    
    def __init__(self, cliente: Cliente, servicio: Servicio, duracion_horas: float, fecha: datetime.datetime = None):
        Reserva._contador_reservas += 1
        self._id_reserva = f"RES-{Reserva._contador_reservas:04d}"
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._fecha = fecha if fecha else datetime.datetime.now()
        self._estado = "PENDIENTE"
        
        servicio.validar_parametros(duracion_horas=duracion_horas)
        logging.info(f"Reserva creada: {self._id_reserva}")
    
    def calcular_costo_total(self, descuento: float = 0.0, impuesto: bool = False) -> float:
        return self._servicio.calcular_costo(self._duracion_horas, descuento=descuento, aplicar_impuesto=impuesto)
    
    def confirmar(self) -> bool:
        if self._estado != "PENDIENTE":
            raise ReservaInvalidaError(f"No se puede confirmar reserva en estado {self._estado}")
        self._estado = "CONFIRMADA"
        return True
    
    def cancelar(self) -> bool:
        if self._estado == "COMPLETADA":
            raise ReservaInvalidaError("No se puede cancelar una reserva completada")
        self._estado = "CANCELADA"
        return True
    
    def completar(self) -> bool:
        if self._estado == "CONFIRMADA":
            self._estado = "COMPLETADA"
            return True
        raise ReservaInvalidaError(f"No se puede completar reserva en estado {self._estado}")
    
    def obtener_info(self) -> dict:
        return {
            "ID": self._id_reserva,
            "Cliente": self._cliente.get_nombre(),
            "Servicio": self._servicio.get_nombre(),
            "Duración": f"{self._duracion_horas} h",
            "Fecha": self._fecha.strftime('%Y-%m-%d %H:%M'),
            "Estado": self._estado,
            "Costo": f"${self.calcular_costo_total():,.0f}"
        }

# ========================= SISTEMA DE GESTIÓN =========================
class SistemaGestion:
    def __init__(self):
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        self._cargar_servicios_predeterminados()
    
    def _cargar_servicios_predeterminados(self):
        servicios_def = [
            ReservaSalas("S001", "Sala Ejecutiva", 50000, 20),
            ReservaSalas("S002", "Sala de Conferencias", 80000, 50),
            AlquilerEquipos("E001", "Laptop HP", 15000, "Portátil"),
            AlquilerEquipos("E002", "Proyector Epson", 25000, "Multimedia"),
            AsesoriasEspecializadas("A001", "Python Avanzado", 80000, "Programación"),
            AsesoriasEspecializadas("A002", "Bases de Datos", 70000, "SQL")
        ]
        for s in servicios_def:
            self._servicios.append(s)
    
    def registrar_cliente(self, id_cliente: str, nombre: str, email: str, telefono: str) -> Optional[Cliente]:
        try:
            for c in self._clientes:
                if c.get_id() == id_cliente:
                    raise ClienteInvalidoError(f"Ya existe cliente con ID {id_cliente}")
            cliente = Cliente(id_cliente, nombre, email, telefono)
            self._clientes.append(cliente)
            return cliente
        except Exception as e:
            logging.error(f"Error registrar cliente: {str(e)}")
            raise
    
    def crear_reserva(self, id_cliente: str, id_servicio: str, duracion_horas: float) -> Optional[Reserva]:
        cliente = next((c for c in self._clientes if c.get_id() == id_cliente), None)
        if not cliente:
            raise ReservaInvalidaError(f"Cliente {id_cliente} no encontrado")
        
        servicio = next((s for s in self._servicios if s.get_id() == id_servicio), None)
        if not servicio:
            raise ReservaInvalidaError(f"Servicio {id_servicio} no encontrado")
        
        reserva = Reserva(cliente, servicio, duracion_horas)
        self._reservas.append(reserva)
        return reserva
    
    def listar_clientes(self) -> List[Cliente]:
        return self._clientes.copy()
    
    def listar_servicios(self) -> List[Servicio]:
        return self._servicios.copy()
    
    def listar_reservas(self) -> List[Reserva]:
        return self._reservas.copy()

# ========================= INTERFAZ GRÁFICA PROFESIONAL =========================
class AplicacionSistema:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Sistema de Gestión Empresarial")
        self.root.geometry("1280x720")
        self.root.configure(bg="#1e1e2f")
        
        # Estilos profesionales
        self.colores = {
            "bg_principal": "#1e1e2f",
            "bg_secundario": "#2d2d3f",
            "acento": "#4a6fa5",
            "acento_hover": "#5b7fb5",
            "texto": "#ffffff",
            "texto_secundario": "#a0a0b0",
            "exito": "#4caf50",
            "peligro": "#f44336",
            "advertencia": "#ff9800"
        }
        
        self.sistema = SistemaGestion()
        self._configurar_estilos()
        self._crear_interfaz()
        self._cargar_datos_ejemplo()
    
    def _configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=self.colores["bg_principal"])
        style.configure("TLabel", background=self.colores["bg_principal"], foreground=self.colores["texto"])
        style.configure("TButton", background=self.colores["acento"], foreground="white", borderwidth=0, focuscolor="none", font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", self.colores["acento_hover"])])
        style.configure("Treeview", background=self.colores["bg_secundario"], foreground=self.colores["texto"], fieldbackground=self.colores["bg_secundario"], font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background=self.colores["acento"], foreground="white", font=("Segoe UI", 10, "bold"))
    
    def _crear_interfaz(self):
        # Barra superior
        header = tk.Frame(self.root, bg=self.colores["acento"], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        titulo = tk.Label(header, text="🏢 SOFTWARE FJ - SISTEMA INTEGRAL DE GESTIÓN", font=("Segoe UI", 18, "bold"), bg=self.colores["acento"], fg="white")
        titulo.pack(pady=15)
        
        # Panel de pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear pestañas
        self._crear_pestana_clientes()
        self._crear_pestana_servicios()
        self._crear_pestana_reservas()
        self._crear_pestana_logs()
    
    def _crear_pestana_clientes(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👥 CLIENTES")
        
        # Panel izquierdo - Formulario
        panel_form = tk.Frame(tab, bg=self.colores["bg_secundario"], relief="ridge", bd=2)
        panel_form.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)
        
        tk.Label(panel_form, text="REGISTRAR CLIENTE", font=("Segoe UI", 14, "bold"), bg=self.colores["bg_secundario"], fg=self.colores["acento"]).pack(pady=10)
        
        campos = [
            ("ID Cliente:", "id_cliente"),
            ("Nombre completo:", "nombre"),
            ("Email:", "email"),
            ("Teléfono:", "telefono")
        ]
        
        self.entries_clientes = {}
        for label, key in campos:
            frame = tk.Frame(panel_form, bg=self.colores["bg_secundario"])
            frame.pack(fill="x", pady=5)
            tk.Label(frame, text=label, width=15, anchor="w", bg=self.colores["bg_secundario"], fg=self.colores["texto"]).pack(side="left")
            entry = tk.Entry(frame, width=25, font=("Segoe UI", 10), bg="#3d3d50", fg="white", insertbackground="white")
            entry.pack(side="left", padx=5)
            self.entries_clientes[key] = entry
        
        btn_guardar = tk.Button(panel_form, text="✅ REGISTRAR CLIENTE", bg=self.colores["exito"], fg="white", font=("Segoe UI", 11, "bold"), command=self._registrar_cliente)
        btn_guardar.pack(pady=15, fill="x")
        
        # Panel derecho - Lista de clientes
        panel_lista = tk.Frame(tab, bg=self.colores["bg_secundario"])
        panel_lista.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(panel_lista, text="LISTA DE CLIENTES", font=("Segoe UI", 14, "bold"), bg=self.colores["bg_secundario"], fg=self.colores["acento"]).pack(pady=10)
        
        self.tree_clientes = ttk.Treeview(panel_lista, columns=("ID", "Nombre", "Email", "Teléfono"), show="headings", height=15)
        self.tree_clientes.heading("ID", text="ID")
        self.tree_clientes.heading("Nombre", text="Nombre")
        self.tree_clientes.heading("Email", text="Email")
        self.tree_clientes.heading("Teléfono", text="Teléfono")
        self.tree_clientes.column("ID", width=80)
        self.tree_clientes.column("Nombre", width=200)
        self.tree_clientes.column("Email", width=200)
        self.tree_clientes.column("Teléfono", width=120)
        self.tree_clientes.pack(fill="both", expand=True)
        
        scroll = ttk.Scrollbar(panel_lista, orient="vertical", command=self.tree_clientes.yview)
        scroll.pack(side="right", fill="y")
        self.tree_clientes.configure(yscrollcommand=scroll.set)
    
    def _crear_pestana_servicios(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🛠️ SERVICIOS")
        
        # Treeview para servicios
        panel = tk.Frame(tab, bg=self.colores["bg_secundario"])
        panel.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(panel, text="SERVICIOS DISPONIBLES", font=("Segoe UI", 14, "bold"), bg=self.colores["bg_secundario"], fg=self.colores["acento"]).pack(pady=10)
        
        self.tree_servicios = ttk.Treeview(panel, columns=("ID", "Nombre", "Tipo", "Precio Base"), show="headings", height=20)
        self.tree_servicios.heading("ID", text="ID")
        self.tree_servicios.heading("Nombre", text="Nombre")
        self.tree_servicios.heading("Tipo", text="Tipo")
        self.tree_servicios.heading("Precio Base", text="Precio Base")
        self.tree_servicios.column("ID", width=80)
        self.tree_servicios.column("Nombre", width=250)
        self.tree_servicios.column("Tipo", width=200)
        self.tree_servicios.column("Precio Base", width=120)
        self.tree_servicios.pack(fill="both", expand=True)
        
        self._actualizar_lista_servicios()
    
    def _crear_pestana_reservas(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📅 RESERVAS")
        
        # Panel superior - Crear reserva
        panel_crear = tk.Frame(tab, bg=self.colores["bg_secundario"], relief="ridge", bd=2)
        panel_crear.pack(fill="x", padx=10, pady=10, ipady=10)
        
        tk.Label(panel_crear, text="CREAR NUEVA RESERVA", font=("Segoe UI", 14, "bold"), bg=self.colores["bg_secundario"], fg=self.colores["acento"]).pack(pady=5)
        
        frame_fila = tk.Frame(panel_crear, bg=self.colores["bg_secundario"])
        frame_fila.pack(pady=5)
        
        tk.Label(frame_fila, text="Cliente ID:", bg=self.colores["bg_secundario"], fg=self.colores["texto"]).pack(side="left", padx=5)
        self.combo_clientes = ttk.Combobox(frame_fila, width=20, font=("Segoe UI", 10))
        self.combo_clientes.pack(side="left", padx=5)
        
        tk.Label(frame_fila, text="Servicio ID:", bg=self.colores["bg_secundario"], fg=self.colores["texto"]).pack(side="left", padx=5)
        self.combo_servicios = ttk.Combobox(frame_fila, width=20, font=("Segoe UI", 10))
        self.combo_servicios.pack(side="left", padx=5)
        
        tk.Label(frame_fila, text="Duración (h):", bg=self.colores["bg_secundario"], fg=self.colores["texto"]).pack(side="left", padx=5)
        self.entry_duracion = tk.Entry(frame_fila, width=10, font=("Segoe UI", 10), bg="#3d3d50", fg="white")
        self.entry_duracion.pack(side="left", padx=5)
        
        btn_crear = tk.Button(frame_fila, text="📌 CREAR RESERVA", bg=self.colores["exito"], fg="white", font=("Segoe UI", 10, "bold"), command=self._crear_reserva)
        btn_crear.pack(side="left", padx=20)
        
        # Panel medio - Acciones
        panel_acciones = tk.Frame(tab, bg=self.colores["bg_secundario"])
        panel_acciones.pack(fill="x", padx=10, pady=5)
        
        btn_confirmar = tk.Button(panel_acciones, text="✅ Confirmar", bg=self.colores["exito"], fg="white", command=self._confirmar_reserva)
        btn_confirmar.pack(side="left", padx=5, pady=5)
        
        btn_cancelar = tk.Button(panel_acciones, text="❌ Cancelar", bg=self.colores["peligro"], fg="white", command=self._cancelar_reserva)
        btn_cancelar.pack(side="left", padx=5, pady=5)
        
        btn_completar = tk.Button(panel_acciones, text="🏁 Completar", bg=self.colores["advertencia"], fg="white", command=self._completar_reserva)
        btn_completar.pack(side="left", padx=5, pady=5)
        
        btn_refrescar = tk.Button(panel_acciones, text="🔄 Refrescar", bg=self.colores["acento"], fg="white", command=self._actualizar_lista_reservas)
        btn_refrescar.pack(side="right", padx=5, pady=5)
        
        # Panel inferior - Lista de reservas
        panel_lista = tk.Frame(tab, bg=self.colores["bg_secundario"])
        panel_lista.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(panel_lista, text="LISTA DE RESERVAS", font=("Segoe UI", 12, "bold"), bg=self.colores["bg_secundario"], fg=self.colores["acento"]).pack(pady=5)
        
        self.tree_reservas = ttk.Treeview(panel_lista, columns=("ID", "Cliente", "Servicio", "Duración", "Fecha", "Estado", "Costo"), show="headings", height=12)
        for col in self.tree_reservas["columns"]:
            self.tree_reservas.heading(col, text=col)
            self.tree_reservas.column(col, width=120 if col != "Servicio" else 150)
        self.tree_reservas.pack(fill="both", expand=True)
    
    def _crear_pestana_logs(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📋 LOGS DEL SISTEMA")
        
        panel = tk.Frame(tab, bg=self.colores["bg_secundario"])
        panel.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(panel, text="REGISTRO DE EVENTOS Y ERRORES", font=("Segoe UI", 12, "bold"), bg=self.colores["bg_secundario"], fg=self.colores["acento"]).pack(pady=5)
        
        self.text_logs = scrolledtext.ScrolledText(panel, wrap=tk.WORD, width=100, height=25, bg="#1e1e2f", fg="#00ff00", font=("Consolas", 9), insertbackground="white")
        self.text_logs.pack(fill="both", expand=True)
        
        btn_refrescar = tk.Button(panel, text="🔄 Refrescar Logs", bg=self.colores["acento"], fg="white", command=self._actualizar_logs)
        btn_refrescar.pack(pady=5)
        
        self._actualizar_logs()
    
    def _cargar_datos_ejemplo(self):
        try:
            self.sistema.registrar_cliente("C001", "Ana María Rodríguez", "ana@email.com", "3001234567")
            self.sistema.registrar_cliente("C002", "Carlos López", "carlos@email.com", "3119876543")
            self.sistema.registrar_cliente("C003", "María García", "maria@email.com", "3225558877")
        except:
            pass
        self._actualizar_lista_clientes()
        self._actualizar_combos()
    
    def _registrar_cliente(self):
        try:
            id_cliente = self.entries_clientes["id_cliente"].get().strip()
            nombre = self.entries_clientes["nombre"].get().strip()
            email = self.entries_clientes["email"].get().strip()
            telefono = self.entries_clientes["telefono"].get().strip()
            
            if not all([id_cliente, nombre, email, telefono]):
                messagebox.showwarning("Campos incompletos", "Por favor complete todos los campos")
                return
            
            self.sistema.registrar_cliente(id_cliente, nombre, email, telefono)
            self._actualizar_lista_clientes()
            self._actualizar_combos()
            
            for entry in self.entries_clientes.values():
                entry.delete(0, tk.END)
            
            messagebox.showinfo("Éxito", f"Cliente {nombre} registrado correctamente")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _actualizar_lista_clientes(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        for cliente in self.sistema.listar_clientes():
            self.tree_clientes.insert("", "end", values=(cliente.get_id(), cliente.get_nombre(), cliente.get_email(), cliente.get_telefono()))
    
    def _actualizar_lista_servicios(self):
        for item in self.tree_servicios.get_children():
            self.tree_servicios.delete(item)
        
        for servicio in self.sistema.listar_servicios():
            tipo = type(servicio).__name__
            self.tree_servicios.insert("", "end", values=(servicio.get_id(), servicio.get_nombre(), tipo, f"${servicio.get_precio_base():,.0f}"))
    
    def _actualizar_combos(self):
        clientes = [c.get_id() for c in self.sistema.listar_clientes()]
        servicios = [s.get_id() for s in self.sistema.listar_servicios()]
        self.combo_clientes['values'] = clientes
        self.combo_servicios['values'] = servicios
    
    def _crear_reserva(self):
        try:
            id_cliente = self.combo_clientes.get()
            id_servicio = self.combo_servicios.get()
            duracion = float(self.entry_duracion.get())
            
            if not id_cliente or not id_servicio:
                messagebox.showwarning("Datos incompletos", "Seleccione cliente y servicio")
                return
            
            reserva = self.sistema.crear_reserva(id_cliente, id_servicio, duracion)
            self._actualizar_lista_reservas()
            messagebox.showinfo("Éxito", f"Reserva {reserva._id_reserva} creada exitosamente")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _actualizar_lista_reservas(self):
        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)
        
        for reserva in self.sistema.listar_reservas():
            info = reserva.obtener_info()
            self.tree_reservas.insert("", "end", values=(info["ID"], info["Cliente"], info["Servicio"], info["Duración"], info["Fecha"], info["Estado"], info["Costo"]))
    
    def _obtener_reserva_seleccionada(self):
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Seleccione una reserva")
            return None
        
        valores = self.tree_reservas.item(seleccion[0])['values']
        id_reserva = valores[0]
        
        for reserva in self.sistema.listar_reservas():
            if reserva._id_reserva == id_reserva:
                return reserva
        return None
    
    def _confirmar_reserva(self):
        reserva = self._obtener_reserva_seleccionada()
        if reserva:
            try:
                reserva.confirmar()
                self._actualizar_lista_reservas()
                messagebox.showinfo("Éxito", "Reserva confirmada")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _cancelar_reserva(self):
        reserva = self._obtener_reserva_seleccionada()
        if reserva:
            try:
                reserva.cancelar()
                self._actualizar_lista_reservas()
                messagebox.showinfo("Éxito", "Reserva cancelada")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _completar_reserva(self):
        reserva = self._obtener_reserva_seleccionada()
        if reserva:
            try:
                reserva.completar()
                self._actualizar_lista_reservas()
                messagebox.showinfo("Éxito", "Reserva completada")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def _actualizar_logs(self):
        self.text_logs.delete(1.0, tk.END)
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                contenido = f.read()
                self.text_logs.insert(tk.END, contenido)
        else:
            self.text_logs.insert(tk.END, "No hay archivo de logs aún")

# ========================= PUNTO DE ENTRADA =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionSistema(root)
    root.mainloop()