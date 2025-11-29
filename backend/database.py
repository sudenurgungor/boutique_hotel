import psycopg2
from psycopg2 import Error
import tkinter.messagebox as mb
import config

last_error = None


def _handle_error(prefix: str, e: Exception):
    """
    Hataları konsola ve mesaj kutusuna yaz.
    """
    global last_error
    last_error = f"{prefix} {e}"
    try:
        print(last_error)
    except Exception:
        pass
    try:
        mb.showerror("Veritabanı Hatası", last_error)
    except Exception:
        pass


def get_connection():
    """
    PostgreSQL veritabanına bağlanır ve connection nesnesi döndürür.
    """
    conn = psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT,
    )
    return conn
