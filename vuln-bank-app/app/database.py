import sqlite3
import os

# Define la ruta de la base de datos que está en el volumen
DATABASE_PATH = '/app/data/app.db'

def init_database():
    """
    Inicializa la base de datos con las tablas y datos de prueba.
    Esta función se llama al inicio de app.py.
    """
    # Vulnerabilidad: conexión a BD sin parámetros seguros (aunque en SQLite local es menos crítico)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Crear tablas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            is_admin INTEGER,
            balance REAL,
            ssn TEXT
        )
    ''')
    
    # Insertar usuarios de prueba si no existen
    cursor.execute("SELECT COUNT(*) FROM user")
    if cursor.fetchone()[0] == 0:
        users = [
            (1, 'admin', 'admin123', 'admin@securebank.com', 1, 1000000.0, '123-45-6789'),
            (2, 'alice', 'password123', 'alice@securebank.com', 0, 5000.0, '987-65-4321'),
            (3, 'bob', 'qwerty', 'bob@securebank.com', 0, 3000.0, '456-78-9123')
        ]
        # Nota: Usando VALUES directamente para insertar, ya que es la inicialización.
        cursor.executemany('INSERT INTO user VALUES (?,?,?,?,?,?,?)', users)
        
    conn.commit()
    conn.close()

def unsafe_query(query):
    """
    Función intencionalmente vulnerable a SQLi (Inyección SQL).
    Se usa para las rutas /search y /login.
    """
    # VULNERABILIDAD: Ejecución directa de consulta sin sanitización ni parámetros. 
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute(query) 
        results = cursor.fetchall()
    except sqlite3.OperationalError as e:
        results = None
        # Envolviendo el error para debug
        raise Exception(f"SQL Error during execution: {e} | Query: {query}")
        
    conn.close()
    return results
