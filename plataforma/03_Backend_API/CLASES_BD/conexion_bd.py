# Back-End/CLASES_BD/conexion_bd.py
import pyodbc

# Configuración de tu SQL Server
DB_CONFIG = {
    'server': 'localhost',  # Cambia esto si tu servidor tiene otro nombre en SSMS
    'database': 'NightWatch_DB',
    'driver': '{ODBC Driver 17 for SQL Server}',
    'trusted_connection': 'yes'
}

def conectar_bd():
    """Establece y retorna la conexión con SQL Server"""
    try:
        string_conexion = f"DRIVER={DB_CONFIG['driver']};SERVER={DB_CONFIG['server']};DATABASE={DB_CONFIG['database']};Trusted_Connection={DB_CONFIG['trusted_connection']};"
        conexion = pyodbc.connect(string_conexion)
        return conexion
    except Exception as e:
        print(f"Error al conectar a la Base de Datos: {e}")
        return None