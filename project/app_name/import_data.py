import sqlite3
from django.db import transaction
from app_name.models import Juego

def import_juegos_from_sqlite():
    # Conecta a la base de datos SQLite
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Obtiene todos los juegos
    cursor.execute("SELECT * FROM juegos")
    juegos = cursor.fetchall()
    
    # Importa cada juego
    with transaction.atomic():
        for juego in juegos:
            Juego.objects.create(
                url=juego[0],          # url
                nombre=juego[1],       # nombre
                precio=juego[2],       # precio
                generos=juego[3],      # generos
                tags=juego[4],         # tags
                companias=juego[5],    # companias
                fecha_lanzamiento=juego[6],  # fecha_lanzamiento
                sistema_operativo=juego[7],  # sistema_operativo
                calificacion=juego[8], # calificacion
                img=juego[9]           # img
            )
    
    print(f"Se importaron {len(juegos)} juegos")

if __name__ == "__main__":
    import_juegos_from_sqlite()