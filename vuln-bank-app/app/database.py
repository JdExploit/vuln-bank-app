import sqlite3
import os

def init_database():
    # Vulnerabilidad: conexión a BD sin parámetros seguros
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Crear tablas con SQL directo (vulnerable)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            credit_card TEXT,
            ssn TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            user TEXT,
            action TEXT,
            ip TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def unsafe_query(query):
    # Función intencionalmente vulnerable a SQLi
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute(query)  # ¡NUNCA hacer esto en producción!
    results = cursor.fetchall()
    conn.close()
    return results