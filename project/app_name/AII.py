from bs4 import BeautifulSoup
import urllib.request
import re
import shutil
import whoosh
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, NUMERIC, KEYWORD, ID
import sqlite3
import os
import ssl

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def almacenar_datos():
    # Definir el esquema
    schema = Schema(
        url=ID(stored=True),
        nombre=TEXT(stored=True),
        precio=NUMERIC(stored=True, numtype=float),
        generos=KEYWORD(stored=True, commas=True),
        tags=KEYWORD(stored=True, commas=True),
        companias=KEYWORD(stored=True, commas=True),
        fecha_lanzamiento=TEXT(stored=True),
        sistema_operativo=TEXT(stored=True),
        calificacion=NUMERIC(stored=True, numtype=float)
    )

    # Crear carpeta del índice
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    # Crear índice Whoosh
    ix = create_in("Index", schema=schema)
    writer = ix.writer()
    
    lista = almacenar_juegos()
    for juego in lista:
        writer.add_document(
            url=str(juego[0]),
            nombre=str(juego[1]),
            precio=float(juego[2]),
            generos=",".join(juego[3]),
            tags=",".join(juego[4]),
            companias=",".join(juego[5]),
            fecha_lanzamiento=juego[6],
            sistema_operativo=str(juego[7]),
            calificacion=float(juego[8])
        )
    writer.commit()
    guardar_en_sqlite(lista)
    print(f"Se han indexado y guardado {len(lista)} juegos.")

def almacenar_juegos():
    f = urllib.request.urlopen("https://www.gog.com/en/games")
    soup = BeautifulSoup(f, "lxml")
    datos = soup.find("div", class_="paginated-products-grid grid").find_all("product-tile")

    lista = []
    for juego in datos: 
        generos = []
        tags = []
        companias = []
        url = juego.find("a")["href"]
        print("Procesando:", url)

        f2 = urllib.request.urlopen(url)
        soup2 = BeautifulSoup(f2, "lxml")

        nombre = soup2.find("h1", class_="productcard-basics__title").text.strip()

        precio = soup2.find(attrs={"selenium-id": "ProductFinalPrice"}).text.strip()

        genero = soup2.find("div", class_="details__content table__row-content").find_all("a")
        for i in genero:
            generos.append(i.text)

        tag = soup2.find(attrs={"selenium-id": "ProductTags"}).find("div", class_="details__content table__row-content").find_all("span", class_="details__link-text")
        for i in tag:
            tags.append(i.text)

        compania = soup2.find("div", class_="table__row details__rating details__row").next_sibling.next_sibling.find_all("a")
        for i in compania:
            companias.append(i.text)

        FechasinParseado = soup2.find("div", class_="table__row details__rating details__row").next_sibling.text.strip()
        match = re.search(r"(\d{4}-\d{2}-\d{2})", FechasinParseado)
        Fecha = match.group(1) if match else "0000-00-00"

        SistemaOperativo = soup2.find("div", class_="table__row details__rating details__row").find("div", class_="details__content table__row-content").text.strip()

        if soup2.find("div", class_="rating productcard-rating__score") is not None:
            OverallRating = soup2.find("div", class_="rating productcard-rating__score").text.strip().split("/")[0]
        else:
            OverallRating = 0.0

        lista.append((url, nombre, precio, generos, tags, companias, Fecha, SistemaOperativo, OverallRating))
    return lista

def guardar_en_sqlite(lista):
    conn = sqlite3.connect("db.sqlite3")
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
            calificacion REAL
        )
    ''')

    for juego in lista:
        c.execute('''
            INSERT OR REPLACE INTO juegos (
                url, nombre, precio, generos, tags, companias, 
                fecha_lanzamiento, sistema_operativo, calificacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            juego[0],
            juego[1],
            float(juego[2].replace("$", "").replace("Free", "0").strip()),
            ",".join(juego[3]),
            ",".join(juego[4]),
            ",".join(juego[5]),
            juego[6],
            juego[7],
            float(juego[8]) if juego[8] else 0.0
        ))

    conn.commit()
    conn.close()
    print(f"Se han guardado {len(lista)} juegos en SQLite.")

# Ejecutar automáticamente
if __name__ == "__main__":
    almacenar_datos()
