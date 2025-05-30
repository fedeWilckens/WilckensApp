import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image
import sqlite3
from datetime import datetime
import pandas as pd
import os
import qrcode

class BreweryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wilckens Lagers - Gestión de Cervecería")
        self.root.geometry("1200x700")
        self.bg_color = "#2B2B2B"
        self.text_color = "#FFFFFF"
        self.accent_color = "#8B6F47"
        ctk.set_appearance_mode("dark")
        self.root.configure(bg=self.bg_color)
        self.conn = sqlite3.connect("brewery.db")
        self.create_tables()
        self.setup_ui()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS barrels (
                id TEXT PRIMARY KEY,
                capacity REAL,
                status TEXT,
                client_id TEXT,
                start_date TEXT,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY,
                name TEXT,
                contact TEXT,
                address TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id TEXT PRIMARY KEY,
                client_id TEXT,
                amount REAL,
                status TEXT,
                issue_date TEXT,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                invoice_id TEXT,
                amount REAL,
                payment_date TEXT,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batches (
                id TEXT PRIMARY KEY,
                product_name TEXT,
                volume REAL,
                start_date TEXT,
                status TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fermenters (
                id TEXT PRIMARY KEY,
                capacity REAL,
                status TEXT,
                batch_id TEXT,
                start_date TEXT,
                FOREIGN KEY (batch_id) REFERENCES batches(id)
            )
        """)
        self.conn.commit()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.bg_color)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        try:
            logo_image = Image.open("logo.png").resize((100, 100))
        except FileNotFoundError:
            logo_image = Image.new("RGB", (100, 100), color="#2B2B2B")
        self.logo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(100, 100))
        logo_label = ctk.CTkLabel(self.main_frame, image=self.logo, text="")
        logo_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="Wilckens Lagers - Gestión de Cervecería", 
            font=("Arial", 24, "bold"), 
            text_color=self.text_color
        )
        title_label.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        
        self.tab_view = ctk.CTkTabview(
            self.main_frame, 
            fg_color="#2B2B2B", 
            text_color=self.text_color, 
            segmented_button_fg_color="#8B6F47",
            segmented_button_selected_color="#A68A64",
            segmented_button_selected_hover_color="#B89B7A"
        )
        self.tab_view.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        self.tab_view.add("Barriles")
        self.tab_view.add("Clientes")
        self.tab_view.add("Facturas")
        self.tab_view.add("Lotes")
        self.tab_view.add("Fermentadores")
        
        self.setup_barrels_tab()
        self.setup_clients_tab()
        self.setup_invoices_tab()
        self.setup_batches_tab()
        self.setup_fermenters_tab()

    def smooth_scroll(self, widget, event, horizontal=False):
        delta = -1 if event.delta > 0 else 1
        if horizontal:
            widget.xview_scroll(delta, "units")
        else:
            widget.yview_scroll(delta, "units")

    def setup_barrels_tab(self):
        tab = self.tab_view.tab("Barriles")
        input_frame = ctk.CTkFrame(tab, fg_color=self.bg_color)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        icon_label = ctk.CTkLabel(input_frame, text="[Icono Barriles]", font=("Arial", 14), text_color=self.text_color)
        icon_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(input_frame, text="ID del Barril:", text_color=self.text_color).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.barrel_id_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.barrel_id_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Capacidad (litros):", text_color=self.text_color).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.barrel_capacity_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.barrel_capacity_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Estado:", text_color=self.text_color).grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.barrel_status_var = ctk.StringVar(value="Libre")
        self.barrel_status_combobox = ctk.CTkComboBox(
            input_frame, values=["Ocupado", "Libre", "En Limpieza"], variable=self.barrel_status_var, 
            width=200, fg_color="#2B2B2B", text_color=self.text_color, button_color=self.accent_color,
            button_hover_color="#A68A64"
        )
        self.barrel_status_combobox.grid(row=1, column=3, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="ID del Cliente:", text_color=self.text_color).grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.barrel_client_id_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.barrel_client_id_entry.grid(row=2, column=3, padx=10, pady=5)
        
        ctk.CTkButton(input_frame, text="Agregar Barril", command=self.load_barrels, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=3, column=0, columnspan=2, pady=15)
        ctk.CTkButton(input_frame, text="Eliminar Barril", command=self.delete_barrel, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=3, column=2, columnspan=2, pady=15)
        ctk.CTkButton(input_frame, text="Procesar QR", command=self.process_qr_code, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=4, column=0, columnspan=2, pady=10)
        ctk.CTkButton(input_frame, text="Generar QR", command=self.generate_barrel_qr, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=4, column=2, columnspan=2, pady=10)
        
        search_frame = ctk.CTkFrame(tab, fg_color=self.bg_color)
        search_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(search_frame, text="Buscar:", text_color=self.text_color).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.barrel_search_entry = ctk.CTkEntry(search_frame, width=300, fg_color="#2B2B2B", text_color=self.text_color)
        self.barrel_search_entry.grid(row=0, column=1, padx=10, pady=5)
        self.barrel_search_entry.bind("<KeyRelease>", self.search_barrels)
        ctk.CTkButton(search_frame, text="Exportar a CSV", command=self.export_barrels, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=0, column=2, padx=10, pady=5)
        
        self.barrel_tree = ttk.Treeview(
            tab, columns=("ID", "Capacity", "Status", "Client ID", "Start Date"), show="headings", 
            style="Treeview", height=15
        )
        self.barrel_tree.heading("ID", text="ID del Barril")
        self.barrel_tree.heading("Capacity", text="Capacidad (L)")
        self.barrel_tree.heading("Status", text="Estado")
        self.barrel_tree.heading("Client ID", text="ID del Cliente")
        self.barrel_tree.heading("Start Date", text="Fecha de Inicio")
        self.barrel_tree.column("ID", width=150)
        self.barrel_tree.column("Capacity", width=150)
        self.barrel_tree.column("Status", width=150)
        self.barrel_tree.column("Client ID", width=150)
        self.barrel_tree.column("Start Date", width=150)
        self.barrel_tree.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        tab.grid_rowconfigure(2, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        v_scrollbar = ctk.CTkScrollbar(tab, orientation="vertical", command=self.barrel_tree.yview, fg_color="#2B2B2B", button_color="#8B6F47", button_hover_color="#A68A64")
        v_scrollbar.grid(row=2, column=1, sticky="ns")
        self.barrel_tree.configure(yscrollcommand=v_scrollbar.set)
        h_scrollbar = ctk.CTkScrollbar(tab, orientation="horizontal", command=self.barrel_tree.xview, fg_color="#2B2B2B", button_color="#8B6F47", button_hover_color="#A68A64")
        h_scrollbar.grid(row=3, column=0, sticky="ew")
        self.barrel_tree.configure(xscrollcommand=h_scrollbar.set)
        
        self.barrel_tree.bind("<MouseWheel>", lambda event: self.smooth_scroll(self.barrel_tree, event))
        self.barrel_tree.bind("<Shift-MouseWheel>", lambda event: self.smooth_scroll(self.barrel_tree, event, horizontal=True))
        self.barrel_tree.bind("<<TreeviewSelect>>", self.select_barrel)
        
        self.update_barrel_table()

    def load_barrels(self):
        barrel_id = self.barrel_id_entry.get()
        capacity = self.barrel_capacity_entry.get()
        status = self.barrel_status_var.get()
        client_id = self.barrel_client_id_entry.get() or None
        start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "Ocupado" else None
        
        if not barrel_id or not capacity:
            messagebox.showerror("Error", "ID y Capacidad son obligatorios")
            return
        try:
            capacity = float(capacity)
            if capacity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La capacidad debe ser un número positivo")
            return
            
        if client_id:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM clients WHERE id=?", (client_id,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "El ID del cliente no existe")
                return
                
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO barrels (id, capacity, status, client_id, start_date) VALUES (?, ?, ?, ?, ?)",
                (barrel_id, capacity, status, client_id, start_date)
            )
            self.conn.commit()
            self.update_barrel_table()
            messagebox.showinfo("Éxito", "Barril agregado correctamente")
            self.clear_barrel_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El ID del barril ya existe")

    def delete_barrel(self):
        barrel_id = self.barrel_id_entry.get()
        if not barrel_id:
            messagebox.showerror("Error", "Ingresa el ID del barril para eliminar")
            return
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM barrels WHERE id=?", (barrel_id,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "El ID del barril no existe")
            return
            
        cursor.execute("DELETE FROM barrels WHERE id=?", (barrel_id,))
        self.conn.commit()
        self.update_barrel_table()
        messagebox.showinfo("Éxito", "Barril eliminado correctamente")
        self.clear_barrel_entries()

    def select_barrel(self, event):
        selected = self.barrel_tree.selection()
        if not selected:
            return
        item = self.barrel_tree.item(selected[0])
        values = item['values']
        self.barrel_id_entry.delete(0, "end")
        self.barrel_id_entry.insert(0, values[0])
        self.barrel_capacity_entry.delete(0, "end")
        self.barrel_capacity_entry.insert(0, values[1])
        self.barrel_status_combobox.set(values[2])
        self.barrel_client_id_entry.delete(0, "end")
        self.barrel_client_id_entry.insert(0, values[3] or "")

    def search_barrels(self, event=None):
        search_term = self.barrel_search_entry.get().lower()
        for item in self.barrel_tree.get_children():
            self.barrel_tree.delete(item)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, capacity, status, client_id, start_date FROM barrels")
        for row in cursor.fetchall():
            if search_term in str(row[0]).lower() or search_term in str(row[2]).lower() or \
               search_term in str(row[3]).lower():
                self.barrel_tree.insert("", "end", values=row)

    def export_barrels(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, capacity, status, client_id, start_date FROM barrels")
            barrels = cursor.fetchall()
            df = pd.DataFrame(barrels, columns=["ID", "Capacidad (L)", "Estado", "ID del Cliente", "Fecha de Inicio"])
            filename = f"barrels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            messagebox.showinfo("Éxito", f"Datos exportados a {filename}")
            os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

    def update_barrel_table(self):
        for item in self.barrel_tree.get_children():
            self.barrel_tree.delete(item)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, capacity, status, client_id, start_date FROM barrels")
        for row in cursor.fetchall():
            self.barrel_tree.insert("", "end", values=row)

    def clear_barrel_entries(self):
        self.barrel_id_entry.delete(0, "end")
        self.barrel_capacity_entry.delete(0, "end")
        self.barrel_status_combobox.set("Libre")
        self.barrel_client_id_entry.delete(0, "end")
        self.barrel_search_entry.delete(0, "end")

    def process_qr_code(self):
        barrel_id = self.barrel_id_entry.get()
        if not barrel_id:
            messagebox.showerror("Error", "Ingresa el ID del barril para procesar el QR")
            return
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, capacity, status, client_id, start_date FROM barrels WHERE id=?", (barrel_id,))
        barrel = cursor.fetchone()
        if not barrel:
            messagebox.showerror("Error", "Barril no encontrado")
            return
            
        messagebox.showinfo("Información del Barril", f"ID: {barrel[0]}\nCapacidad: {barrel[1]} L\nEstado: {barrel[2]}\nCliente: {barrel[3] or 'N/A'}\nFecha: {barrel[4] or 'N/A'}")

    def generate_barrel_qr(self):
        barrel_id = self.barrel_id_entry.get()
        if not barrel_id:
            messagebox.showerror("Error", "Ingresa el ID del barril para generar el QR")
            return
            
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(barrel_id)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")
        filename = f"barrel_qr_{barrel_id}.png"
        img.save(filename)
        messagebox.showinfo("Éxito", f"Código QR generado: {filename}")
        os.startfile(filename)

    def setup_clients_tab(self):
        tab = self.tab_view.tab("Clientes")
        input_frame = ctk.CTkFrame(tab, fg_color=self.bg_color)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        icon_label = ctk.CTkLabel(input_frame, text="[Icono Clientes]", font=("Arial", 14), text_color=self.text_color)
        icon_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(input_frame, text="ID del Cliente:", text_color=self.text_color).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.client_id_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.client_id_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Nombre:", text_color=self.text_color).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.client_name_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.client_name_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Contacto:", text_color=self.text_color).grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.client_contact_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.client_contact_entry.grid(row=1, column=3, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Dirección:", text_color=self.text_color).grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.client_address_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.client_address_entry.grid(row=2, column=3, padx=10, pady=5)
        
        ctk.CTkButton(input_frame, text="Agregar Cliente", command=self.add_client, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=3, column=0, columnspan=2, pady=15)
        ctk.CTkButton(input_frame, text="Eliminar Cliente", command=self.delete_client, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=3, column=2, columnspan=2, pady=15)
        
        search_frame = ctk.CTkFrame(tab, fg_color=self.bg_color)
        search_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(search_frame, text="Buscar:", text_color=self.text_color).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.client_search_entry = ctk.CTkEntry(search_frame, width=300, fg_color="#2B2B2B", text_color=self.text_color)
        self.client_search_entry.grid(row=0, column=1, padx=10, pady=5)
        self.client_search_entry.bind("<KeyRelease>", self.search_clients)
        ctk.CTkButton(search_frame, text="Exportar a CSV", command=self.export_clients, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=0, column=2, padx=10, pady=5)
        
        self.client_tree = ttk.Treeview(
            tab, columns=("ID", "Name", "Contact", "Address"), show="headings", style="Treeview", height=15
        )
        self.client_tree.heading("ID", text="ID del Cliente")
        self.client_tree.heading("Name", text="Nombre")
        self.client_tree.heading("Contact", text="Contacto")
        self.client_tree.heading("Address", text="Dirección")
        self.client_tree.column("ID", width=150)
        self.client_tree.column("Name", width=200)
        self.client_tree.column("Contact", width=200)
        self.client_tree.column("Address", width=250)
        self.client_tree.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        tab.grid_rowconfigure(2, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        v_scrollbar = ctk.CTkScrollbar(tab, orientation="vertical", command=self.client_tree.yview, fg_color="#2B2B2B", button_color="#8B6F47", button_hover_color="#A68A64")
        v_scrollbar.grid(row=2, column=1, sticky="ns")
        self.client_tree.configure(yscrollcommand=v_scrollbar.set)
        h_scrollbar = ctk.CTkScrollbar(tab, orientation="horizontal", command=self.client_tree.xview, fg_color="#2B2B2B", button_color="#8B6F47", button_hover_color="#A68A64")
        h_scrollbar.grid(row=3, column=0, sticky="ew")
        self.client_tree.configure(xscrollcommand=h_scrollbar.set)
        
        self.client_tree.bind("<MouseWheel>", lambda event: self.smooth_scroll(self.client_tree, event))
        self.client_tree.bind("<Shift-MouseWheel>", lambda event: self.smooth_scroll(self.client_tree, event, horizontal=True))
        self.client_tree.bind("<<TreeviewSelect>>", self.select_client)
        
        self.update_client_table()

    def add_client(self):
        client_id = self.client_id_entry.get().strip()
        name = self.client_name_entry.get().strip()
        contact = self.client_contact_entry.get().strip()
        address = self.client_address_entry.get().strip()
        
        if not client_id or not name:
            messagebox.showerror("Error", "ID y Nombre son obligatorios")
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO clients (id, name, contact, address) VALUES (?, ?, ?, ?)",
                (client_id, name, contact, address)
            )
            self.conn.commit()
            self.update_client_table()
            messagebox.showinfo("Éxito", "Cliente agregado correctamente")
            self.clear_client_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El ID del cliente ya existe")

    def delete_client(self):
        client_id = self.client_id_entry.get().strip()
        if not client_id:
            messagebox.showerror("Error", "Ingresa el ID del cliente para eliminar")
            return
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM clients WHERE id=?", (client_id,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "El ID del cliente no existe")
            return
            
        cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
        self.conn.commit()
        self.update_client_table()
        messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
        self.clear_client_entries()

    def select_client(self, event):
        selected = self.client_tree.selection()
        if not selected:
            return
        item = self.client_tree.item(selected[0])
        values = item['values']
        self.client_id_entry.delete(0, "end")
        self.client_id_entry.insert(0, values[0])
        self.client_name_entry.delete(0, "end")
        self.client_name_entry.insert(0, values[1])
        self.client_contact_entry.delete(0, "end")
        self.client_contact_entry.insert(0, values[2])
        self.client_address_entry.delete(0, "end")
        self.client_address_entry.insert(0, values[3])

    def search_clients(self, event=None):
        search_term = self.client_search_entry.get().lower()
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, contact, address FROM clients")
        for row in cursor.fetchall():
            if search_term in str(row[0]).lower() or search_term in str(row[1]).lower():
                self.client_tree.insert("", "end", values=row)

    def export_clients(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, name, contact, address FROM clients")
            clients = cursor.fetchall()
            df = pd.DataFrame(clients, columns=["ID", "Nombre", "Contacto", "Dirección"])
            filename = f"clients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            messagebox.showinfo("Éxito", f"Datos exportados a {filename}")
            os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

    def update_client_table(self):
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, contact, address FROM clients")
        for row in cursor.fetchall():
            self.client_tree.insert("", "end", values=row)

    def clear_client_entries(self):
        self.client_id_entry.delete(0, "end")
        self.client_name_entry.delete(0, "end")
        self.client_contact_entry.delete(0, "end")
        self.client_address_entry.delete(0, "end")
        self.client_search_entry.delete(0, "end")

    def setup_invoices_tab(self):
        tab = self.tab_view.tab("Facturas")
        input_frame = ctk.CTkFrame(tab, fg_color=self.bg_color)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        icon_label = ctk.CTkLabel(input_frame, text="[Icono Facturas]", font=("Arial", 14), text_color=self.text_color)
        icon_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(input_frame, text="ID de Factura:", text_color=self.text_color).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.invoice_id_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.invoice_id_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="ID del Cliente:", text_color=self.text_color).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.invoice_client_id_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.invoice_client_id_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Monto:", text_color=self.text_color).grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.invoice_amount_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.invoice_amount_entry.grid(row=1, column=3, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Estado:", text_color=self.text_color).grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.invoice_status_var = ctk.StringVar(value="Pendiente")
        self.invoice_status_combobox = ctk.CTkComboBox(
            input_frame, values=["Pendiente", "Pagada", "Vencida"], variable=self.invoice_status_var, 
            width=200, fg_color="#2B2B2B", text_color=self.text_color, button_color=self.accent_color,
            button_hover_color="#A68A64"
        )
        self.invoice_status_combobox.grid(row=2, column=3, padx=10, pady=5)
        
        ctk.CTkButton(input_frame, text="Agregar Factura", command=self.add_invoice, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=3, column=0, columnspan=2, pady=15)
        
        payment_frame = ctk.CTkFrame(tab, fg_color=self.bg_color)
        payment_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(payment_frame, text="ID de Pago:", text_color=self.text_color).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.payment_id_entry = ctk.CTkEntry(payment_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.payment_id_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(payment_frame, text="Monto del Pago:", text_color=self.text_color).grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.payment_amount_entry = ctk.CTkEntry(payment_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.payment_amount_entry.grid(row=0, column=3, padx=10, pady=5)
        
        ctk.CTkButton(payment_frame, text="Agregar Pago", command=self.add_payment, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=1, column=0, columnspan=4, pady=15)
        
        search_frame = ctk.CTkFrame(tab, fg_color=self.bg_color)
        search_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(search_frame, text="Buscar:", text_color=self.text_color).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.invoice_search_entry = ctk.CTkEntry(search_frame, width=300, fg_color="#2B2B2B", text_color=self.text_color)
        self.invoice_search_entry.grid(row=0, column=1, padx=10, pady=5)
        self.invoice_search_entry.bind("<KeyRelease>", self.search_invoices)
        ctk.CTkButton(search_frame, text="Exportar a CSV", command=self.export_invoices, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=0, column=2, padx=10, pady=5)
        
        self.invoice_tree = ttk.Treeview(
            tab, columns=("ID", "Client ID", "Amount", "Status", "Issue Date"), show="headings", 
            style="Treeview", height=15
        )
        self.invoice_tree.heading("ID", text="ID de Factura")
        self.invoice_tree.heading("Client ID", text="ID del Cliente")
        self.invoice_tree.heading("Amount", text="Monto")
        self.invoice_tree.heading("Status", text="Estado")
        self.invoice_tree.heading("Issue Date", text="Fecha de Emisión")
        self.invoice_tree.column("ID", width=150)
        self.invoice_tree.column("Client ID", width=150)
        self.invoice_tree.column("Amount", width=150)
        self.invoice_tree.column("Status", width=150)
        self.invoice_tree.column("Issue Date", width=150)
        self.invoice_tree.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        tab.grid_rowconfigure(3, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        v_scrollbar = ctk.CTkScrollbar(tab, orientation="vertical", command=self.invoice_tree.yview, fg_color="#2B2B2B", button_color="#8B6F47", button_hover_color="#A68A64")
        v_scrollbar.grid(row=3, column=1, sticky="ns")
        self.invoice_tree.configure(yscrollcommand=v_scrollbar.set)
        h_scrollbar = ctk.CTkScrollbar(tab, orientation="horizontal", command=self.invoice_tree.xview, fg_color="#2B2B2B", button_color="#8B6F47", button_hover_color="#A68A64")
        h_scrollbar.grid(row=4, column=0, sticky="ew")
        self.invoice_tree.configure(xscrollcommand=h_scrollbar.set)
        
        self.invoice_tree.bind("<MouseWheel>", lambda event: self.smooth_scroll(self.invoice_tree, event))
        self.invoice_tree.bind("<Shift-MouseWheel>", lambda event: self.smooth_scroll(self.invoice_tree, event, horizontal=True))
        self.invoice_tree.bind("<<TreeviewSelect>>", self.select_invoice)
        
        self.update_invoice_table()

    def add_invoice(self):
        invoice_id = self.invoice_id_entry.get().strip()
        client_id = self.invoice_client_id_entry.get().strip()
        amount = self.invoice_amount_entry.get().strip()
        status = self.invoice_status_var.get()
        issue_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not invoice_id or not client_id or not amount:
            messagebox.showerror("Error", "ID, Cliente y Monto son obligatorios")
            return
            
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número positivo")
            return
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM clients WHERE id=?", (client_id,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "El ID del cliente no existe")
            return
            
        try:
            cursor.execute(
                "INSERT INTO invoices (id, client_id, amount, status, issue_date) VALUES (?, ?, ?, ?, ?)",
                (invoice_id, client_id, amount, status, issue_date)
            )
            self.conn.commit()
            self.update_invoice_table()
            messagebox.showinfo("Éxito", "Factura agregada correctamente")
            self.clear_invoice_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El ID de la factura ya existe")

    def add_payment(self):
        payment_id = self.payment_id_entry.get().strip()
        invoice_id = self.invoice_id_entry.get().strip()
        amount = self.payment_amount_entry.get().strip()
        payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not payment_id or not invoice_id or not amount:
            messagebox.showerror("Error", "ID de Pago, Factura y Monto son obligatorios")
            return
            
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número positivo")
            return
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, amount FROM invoices WHERE id=?", (invoice_id,))
        invoice = cursor.fetchone()
        if not invoice:
            messagebox.showerror("Error", "La factura no existe")
            return
            
        try:
            cursor.execute(
                "INSERT INTO payments (id, invoice_id, amount, payment_date) VALUES (?, ?, ?, ?)",
                (payment_id, invoice_id, amount, payment_date)
            )
            cursor.execute(
                "UPDATE invoices SET status = ? WHERE id = ?",
                ("Pagada" if amount >= invoice[1] else "Pendiente", invoice_id)
            )
            self.conn.commit()
            self.update_invoice_table()
            messagebox.showinfo("Éxito", "Pago registrado correctamente")
            self.clear_payment_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El ID del pago ya existe")

    def select_invoice(self, event):
        selected = self.invoice_tree.selection()
        if not selected:
            return
        item = self.invoice_tree.item(selected[0])
        values = item['values']
        self.invoice_id_entry.delete(0, "end")
        self.invoice_id_entry.insert(0, values[0])
        self.invoice_client_id_entry.delete(0, "end")
        self.invoice_client_id_entry.insert(0, values[1])
        self.invoice_amount_entry.delete(0, "end")
        self.invoice_amount_entry.insert(0, values[2])
        self.invoice_status_combobox.set(values[3])

    def search_invoices(self, event=None):
        search_term = self.invoice_search_entry.get().lower()
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, client_id, amount, status, issue_date FROM invoices")
        for row in cursor.fetchall():
            if search_term in str(row[0]).lower() or search_term in str(row[1]).lower():
                self.invoice_tree.insert("", "end", values=row)

    def export_invoices(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, client_id, amount, status, issue_date FROM invoices")
            invoices = cursor.fetchall()
            df = pd.DataFrame(invoices, columns=["ID", "ID del Cliente", "Monto", "Estado", "Fecha de Emisión"])
            filename = f"invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            messagebox.showinfo("Éxito", f"Datos exportados a {filename}")
            os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

    def update_invoice_table(self):
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, client_id, amount, status, issue_date FROM invoices")
        for row in cursor.fetchall():
            self.invoice_tree.insert("", "end", values=row)

    def clear_invoice_entries(self):
        self.invoice_id_entry.delete(0, "end")
        self.invoice_client_id_entry.delete(0, "end")
        self.invoice_amount_entry.delete(0, "end")
        self.invoice_status_combobox.set("Pendiente")
        self.invoice_search_entry.delete(0, "end")

    def clear_payment_entries(self):
        self.payment_id_entry.delete(0, "end")
        self.payment_amount_entry.delete(0, "end")

    def setup_batches_tab(self):
        tab = self.tab_view.tab("Lotes")
        input_frame = ctk.CTkFrame(tab, fg_color=self.bg_color)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        icon_label = ctk.CTkLabel(input_frame, text="[Icono Lotes]", font=("Arial", 14), text_color=self.text_color)
        icon_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(input_frame, text="ID del Lote:", text_color=self.text_color).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.batch_id_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.batch_id_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Nombre del Producto:", text_color=self.text_color).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.batch_name_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.batch_name_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Volumen:", text_color=self.text_color).grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.batch_volume_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.batch_volume_entry.grid(row=1, column=3, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Estado:", text_color=self.text_color).grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.batch_status_var = ctk.StringVar(value="En curso")
        self.batch_status_combobox = ctk.CTkComboBox(
            input_frame, values=["En curso", "Finalizado", "En espera"], variable=self.batch_status_var, 
            width=200, fg_color="#2B2B2B", text_color=self.text_color, button_color=self.accent_color,
            button_hover_color="#A68A64"
        )
        self.batch_status_combobox.grid(row=2, column=3, padx=10, pady=5)
        
        ctk.CTkButton(input_frame, text="Agregar Lote", command=self.add_batch, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=3, column=0, columnspan=2, pady=15)
        ctk.CTkButton(input_frame, text="Eliminar Lote", command=self.delete_batch, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=3, column=2, columnspan=2, pady=15)
        
        search_frame = ctk.CTkFrame(tab, fg_color=self.bg_color)
        search_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(search_frame, text="Buscar:", text_color=self.text_color).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.batch_search_entry = ctk.CTkEntry(search_frame, width=300, fg_color="#2B2B2B", text_color=self.text_color)
        self.batch_search_entry.grid(row=0, column=1, padx=10, pady=5)
        self.batch_search_entry.bind("<KeyRelease>", self.search_batches)
        ctk.CTkButton(search_frame, text="Exportar a CSV", command=self.export_batches, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=0, column=2, padx=10, pady=5)
        
        self.batch_tree = ttk.Treeview(
            tab, columns=("ID", "Product Name", "Volume", "Status", "Start Date"), show="headings", 
            style="Treeview", height=15
        )
        self.batch_tree.heading("ID", text="ID del Lote")
        self.batch_tree.heading("Product Name", text="Nombre del Producto")
        self.batch_tree.heading("Volume", text="Volumen (L)")
        self.batch_tree.heading("Status", text="Estado")
        self.batch_tree.heading("Start Date", text="Fecha de Inicio")
        self.batch_tree.column("ID", width=150)
        self.batch_tree.column("Product Name", width=200)
        self.batch_tree.column("Volume", width=150)
        self.batch_tree.column("Status", width=150)
        self.batch_tree.column("Start Date", width=150)
        self.batch_tree.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        tab.grid_rowconfigure(2, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        v_scrollbar = ctk.CTkScrollbar(tab, orientation="vertical", command=self.batch_tree.yview, fg_color="#2B2B2B", button_color="#8B6F47", button_hover_color="#A68A64")
        v_scrollbar.grid(row=2, column=1, sticky="ns")
        self.batch_tree.configure(yscrollcommand=v_scrollbar.set)
        h_scrollbar = ctk.CTkScrollbar(tab, orientation="horizontal", command=self.batch_tree.xview, fg_color="#2B2B2B", button_color="#8B6F47", button_hover_color="#A68A64")
        h_scrollbar.grid(row=3, column=0, sticky="ew")
        self.batch_tree.configure(xscrollcommand=h_scrollbar.set)
        
        self.batch_tree.bind("<MouseWheel>", lambda event: self.smooth_scroll(self.batch_tree, event))
        self.batch_tree.bind("<Shift-MouseWheel>", lambda event: self.smooth_scroll(self.batch_tree, event, horizontal=True))
        self.batch_tree.bind("<<TreeviewSelect>>", self.select_batch)
        
        self.update_batch_table()

    def add_batch(self):
        batch_id = self.batch_id_entry.get().strip()
        product_name = self.batch_name_entry.get().strip()
        volume = self.batch_volume_entry.get().strip()
        status = self.batch_status_var.get()
        start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not batch_id or not product_name or not volume:
            messagebox.showerror("Error", "ID, Nombre y Volumen son obligatorios")
            return
            
        try:
            volume = float(volume)
            if volume <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El volumen debe ser un número positivo")
            return
            
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO batches (id, product_name, volume, status, start_date) VALUES (?, ?, ?, ?, ?)",
                (batch_id, product_name, volume, status, start_date)
            )
            self.conn.commit()
            self.update_batch_table()
            messagebox.showinfo("Éxito", "Lote agregado correctamente")
            self.clear_batch_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El ID del lote ya existe")

    def delete_batch(self):
        batch_id = self.batch_id_entry.get().strip()
        if not batch_id:
            messagebox.showerror("Error", "Ingresa el ID del lote para eliminar")
            return
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM batches WHERE id=?", (batch_id,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "El ID del lote no existe")
            return
            
        cursor.execute("DELETE FROM batches WHERE id=?", (batch_id,))
        self.conn.commit()
        self.update_batch_table()
        messagebox.showinfo("Éxito", "Lote eliminado correctamente")
        self.clear_batch_entries()

    def select_batch(self, event):
        selected = self.batch_tree.selection()
        if not selected:
            return
        item = self.batch_tree.item(selected[0])
        values = item['values']
        self.batch_id_entry.delete(0, "end")
        self.batch_id_entry.insert(0, values[0])
        self.batch_name_entry.delete(0, "end")
        self.batch_name_entry.insert(0, values[1])
        self.batch_volume_entry.delete(0, "end")
        self.batch_volume_entry.insert(0, values[2])
        self.batch_status_combobox.set(values[3])

    def search_batches(self, event=None):
        search_term = self.batch_search_entry.get().lower()
        for item in self.batch_tree.get_children():
            self.batch_tree.delete(item)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, product_name, volume, status, start_date FROM batches")
        for row in cursor.fetchall():
            if search_term in str(row[0]).lower() or search_term in str(row[1]).lower():
                self.batch_tree.insert("", "end", values=row)

    def export_batches(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, product_name, volume, status, start_date FROM batches")
            batches = cursor.fetchall()
            df = pd.DataFrame(batches, columns=["ID", "Nombre del Producto", "Volumen (L)", "Estado", "Fecha de Inicio"])
            filename = f"batches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            messagebox.showinfo("Éxito", f"Datos exportados a {filename}")
            os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

    def update_batch_table(self):
        for item in self.batch_tree.get_children():
            self.batch_tree.delete(item)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, product_name, volume, status, start_date FROM batches")
        for row in cursor.fetchall():
            self.batch_tree.insert("", "end", values=row)

    def clear_batch_entries(self):
        self.batch_id_entry.delete(0, "end")
        self.batch_name_entry.delete(0, "end")
        self.batch_volume_entry.delete(0, "end")
        self.batch_status_combobox.set("En curso")
        self.batch_search_entry.delete(0, "end")

    def setup_fermenters_tab(self):
        tab = self.tab_view.tab("Fermentadores")
        input_frame = ctk.CTkFrame(tab, fg_color=self.bg_color)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        icon_label = ctk.CTkLabel(input_frame, text="[Icono Fermentadores]", font=("Arial", 14), text_color=self.text_color)
        icon_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(input_frame, text="ID del Fermentador:", text_color=self.text_color).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.fermenter_id_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.fermenter_id_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Capacidad (litros):", text_color=self.text_color).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.fermenter_capacity_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.fermenter_capacity_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="Estado:", text_color=self.text_color).grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.fermenter_status_var = ctk.StringVar(value="Libre")
        self.fermenter_status_combobox = ctk.CTkComboBox(
            input_frame, values=["Ocupado", "Libre", "En Limpieza"], variable=self.fermenter_status_var, 
            width=200, fg_color="#2B2B2B", text_color=self.text_color, button_color=self.accent_color,
            button_hover_color="#A68A64"
        )
        self.fermenter_status_combobox.grid(row=1, column=3, padx=10, pady=5)
        
        ctk.CTkLabel(input_frame, text="ID de Lote:", text_color=self.text_color).grid(row=2, column=2, padx=10, pady=5, sticky="e")
        self.fermenter_batch_id_entry = ctk.CTkEntry(input_frame, width=200, fg_color="#2B2B2B", text_color=self.text_color)
        self.fermenter_batch_id_entry.grid(row=2, column=3, padx=10, pady=5)
        
        ctk.CTkButton(input_frame, text="Agregar Fermentador", command=self.add_fermenter, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=3, column=0, columnspan=2, pady=15)
        ctk.CTkButton(input_frame, text="Eliminar Fermentador", command=self.delete_fermenter, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=3, column=2, columnspan=2, pady=15)
        
        search_frame = ctk.CTkFrame(tab, fg_color=self.bg_color)
        search_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(search_frame, text="Buscar:", text_color=self.text_color).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.fermenter_search_entry = ctk.CTkEntry(search_frame, width=300, fg_color="#2B2B2B", text_color=self.text_color)
        self.fermenter_search_entry.grid(row=0, column=1, padx=10, pady=5)
        self.fermenter_search_entry.bind("<KeyRelease>", self.search_fermenters)
        ctk.CTkButton(search_frame, text="Exportar a CSV", command=self.export_fermenters, fg_color=self.accent_color, hover_color="#A68A64", text_color=self.text_color).grid(row=0, column=2, padx=10, pady=5)
        
        self.fermenter_tree = ttk.Treeview(
            tab, columns=("ID", "Capacity", "Status", "Batch ID", "Start Date"), show="headings", 
            style="Treeview", height=15
        )
        self.fermenter_tree.heading("ID", text="ID del Fermentador")
        self.fermenter_tree.heading("Capacity", text="Capacidad (L)")
        self.fermenter_tree.heading("Status", text="Estado")
        self.fermenter_tree.heading("Batch ID", text="ID de Lote")
        self.fermenter_tree.heading("Start Date", text="Fecha de Inicio")
        self.fermenter_tree.column("ID", width=150)
        self.fermenter_tree.column("Capacity", width=150)
        self.fermenter_tree.column("Status", width=150)
        self.fermenter_tree.column("Batch ID", width=150)
        self.fermenter_tree.column("Start Date", width=150)
        self.fermenter_tree.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        tab.grid_rowconfigure(2, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        v_scrollbar = ctk.CTkScrollbar(tab, orientation="vertical", command=self.fermenter_tree.yview, fg_color="#2B2B2B", button_color="#8B6F47", button_hover_color="#A68A64")
        v_scrollbar.grid(row=2, column=1, sticky="ns")
        self.fermenter_tree.configure(yscrollcommand=v_scrollbar.set)
        h_scrollbar = ctk.CTkScrollbar(tab, orientation="horizontal", command=self.fermenter_tree.xview, fg_color="#2B2B2B", button_color="#8B6F47", button_hover_color="#A68A64")
        h_scrollbar.grid(row=3, column=0, sticky="ew")
        self.fermenter_tree.configure(xscrollcommand=h_scrollbar.set)
        
        self.fermenter_tree.bind("<MouseWheel>", lambda event: self.smooth_scroll(self.fermenter_tree, event))
        self.fermenter_tree.bind("<Shift-MouseWheel>", lambda event: self.smooth_scroll(self.fermenter_tree, event, horizontal=True))
        self.fermenter_tree.bind("<<TreeviewSelect>>", self.select_fermenter)
        
        self.update_fermenter_table()

    def add_fermenter(self):
        fermenter_id = self.fermenter_id_entry.get().strip()
        capacity = self.fermenter_capacity_entry.get().strip()
        status = self.fermenter_status_var.get()
        batch_id = self.fermenter_batch_id_entry.get().strip() or None
        start_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "Ocupado" else None
        
        if not fermenter_id or not capacity:
            messagebox.showerror("Error", "ID y Capacidad son obligatorios")
            return
        try:
            capacity = float(capacity)
            if capacity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La capacidad debe ser un número positivo")
            return
            
        if batch_id:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM batches WHERE id=?", (batch_id,))
            if not cursor.fetchone():
                messagebox.showerror("Error", "El ID de lote no existe")
                return
                
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO fermenters (id, capacity, status, batch_id, start_date) VALUES (?, ?, ?, ?, ?)",
                (fermenter_id, capacity, status, batch_id, start_date)
            )
            self.conn.commit()
            self.update_fermenter_table()
            messagebox.showinfo("Éxito", "Fermentador agregado correctamente")
            self.clear_fermenter_entries()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El ID del fermentador ya existe")

    def delete_fermenter(self):
        fermenter_id = self.fermenter_id_entry.get().strip()
        if not fermenter_id:
            messagebox.showerror("Error", "Ingresa el ID del fermentador para eliminar")
            return
            
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM fermenters WHERE id=?", (fermenter_id,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "El ID del fermentador no existe")
            return
            
        cursor.execute("DELETE FROM fermenters WHERE id=?", (fermenter_id,))
        self.conn.commit()
        self.update_fermenter_table()
        messagebox.showinfo("Éxito", "Fermentador eliminado correctamente")
        self.clear_fermenter_entries()

    def select_fermenter(self, event):
        selected = self.fermenter_tree.selection()
        if not selected:
            return
        item = self.fermenter_tree.item(selected[0])
        values = item['values']
        self.fermenter_id_entry.delete(0, "end")
        self.fermenter_id_entry.insert(0, values[0])
        self.fermenter_capacity_entry.delete(0, "end")
        self.fermenter_capacity_entry.insert(0, values[1])
        self.fermenter_status_combobox.set(values[2])
        self.fermenter_batch_id_entry.delete(0, "end")
        self.fermenter_batch_id_entry.insert(0, values[3] or "")

    def search_fermenters(self, event=None):
        search_term = self.fermenter_search_entry.get().lower()
        for item in self.fermenter_tree.get_children():
            self.fermenter_tree.delete(item)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, capacity, status, batch_id, start_date FROM fermenters")
        for row in cursor.fetchall():
            if search_term in str(row[0]).lower() or search_term in str(row[2]).lower() or \
               search_term in str(row[3]).lower():
                self.fermenter_tree.insert("", "end", values=row)

    def export_fermenters(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, capacity, status, batch_id, start_date FROM fermenters")
            fermenters = cursor.fetchall()
            df = pd.DataFrame(fermenters, columns=["ID", "Capacidad (L)", "Estado", "ID de Lote", "Fecha de Inicio"])
            filename = f"fermenters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            messagebox.showinfo("Éxito", f"Datos exportados a {filename}")
            os.startfile(filename)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")

    def update_fermenter_table(self):
        for item in self.fermenter_tree.get_children():
            self.fermenter_tree.delete(item)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, capacity, status, batch_id, start_date FROM fermenters")
        for row in cursor.fetchall():
            self.fermenter_tree.insert("", "end", values=row)

    def clear_fermenter_entries(self):
        self.fermenter_id_entry.delete(0, "end")
        self.fermenter_capacity_entry.delete(0, "end")
        self.fermenter_status_combobox.set("Libre")
        self.fermenter_batch_id_entry.delete(0, "end")
        self.fermenter_search_entry.delete(0, "end")

if __name__ == "__main__":
    root = ctk.CTk()
    app = BreweryApp(root)
    root.mainloop()
