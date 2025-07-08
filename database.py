import sqlite3
from datetime import datetime

def init_database():
    """Inisialisasi database untuk menyimpan pesanan"""
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    
    # Tabel untuk menyimpan pesanan
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            delivery_address TEXT
        )
    ''')
    
    # Tabel untuk katalog produk
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            description TEXT,
            category TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_order(customer_name, phone_number, product_name, quantity, price, delivery_address=""):
    """Menambah pesanan baru ke database"""
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    
    total_amount = quantity * price
    
    cursor.execute('''
        INSERT INTO orders (customer_name, phone_number, product_name, quantity, price, total_amount, delivery_address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (customer_name, phone_number, product_name, quantity, price, total_amount, delivery_address))
    
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return order_id

def get_all_orders():
    """Mengambil semua pesanan dari database"""
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM orders ORDER BY order_date DESC')
    orders = cursor.fetchall()
    
    conn.close()
    return orders

def update_order_status(order_id, status):
    """Update status pesanan"""
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    
    conn.commit()
    conn.close()

def add_product(name, price, stock, description="", category=""):
    """Menambah produk ke katalog"""
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO products (name, price, stock, description, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, price, stock, description, category))
    
    conn.commit()
    conn.close()

def get_all_products():
    """Mengambil semua produk dari database"""
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    
    conn.close()
    return products

def get_product_by_name(product_name):
    """Mencari produk berdasarkan nama"""
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products WHERE LOWER(name) LIKE LOWER(?)', (f'%{product_name}%',))
    product = cursor.fetchone()
    
    conn.close()
    return product

# Inisialisasi database saat import
init_database()
