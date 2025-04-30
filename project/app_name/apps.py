from django.apps import AppConfig
import sqlite3
import os

class MiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_name'

    def ready(self):
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.sqlite3')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS juegos (
                url TEXT PRIMARY KEY,
                nombre TEXT,
                precio REAL,
                generos TEXT,
                tags TEXT,
                companias TEXT,
                fecha_lanzamiento TEXT,
                sistema_operativo TEXT,
                calificacion REAL,
                img TEXT
            )
        ''')
        conn.commit()
        conn.close()
