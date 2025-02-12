import mysql.connector

DB_HOST = 'if.unismuh.ac.id'
DB_USER = 'root'
DB_PASSWORD = 'mariabelajar'
DB_NAME = 'rag_system'
PORT_NUMBER = 3388

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=PORT_NUMBER
    )
