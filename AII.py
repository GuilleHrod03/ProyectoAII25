from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, shutil
import whoosh
import whoosh.fields
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, NUMERIC, KEYWORD, ID
from whoosh.qparser import QueryParser

from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, ID,NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context 
#Para evitar problemas con BeautifulSoup


root = Tk()
menu = Menu(root)




# Cargar
def almacenar_datos():
    #Creamos el esquema
    schem = Schema(
        url=ID(stored=True),  # URL única para cada juego
        nombre=TEXT(stored=True),  # Nombre del juego
        precio=NUMERIC(stored=True, numtype=float),  # Precio del juego
        generos=KEYWORD(stored=True, commas=True),  # Géneros como palabras clave (pueden ser múltiples)
        tags=KEYWORD(stored=True, commas=True),  # Tags como palabras clave (pueden ser múltiples)
        companias=KEYWORD(stored=True, commas=True),  # Compañías como palabras clave (pueden ser múltiples)
        fecha_lanzamiento=TEXT(stored=True),  # Fecha de lanzamiento
        sistema_operativo=TEXT(stored=True),  # Sistema operativo
        calificacion=NUMERIC(stored=True, numtype=float) # Calificación general
    )
    #Creamos el índice
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")

        #creamos el índice
    ix = create_in("Index", schema=schem)
    #creamos un writer para poder añadir documentos al indice
    writer = ix.writer()
    i=0
    lista=almacenar_juegos()
    for juego in lista:
        writer.add_document(url=str(juego[0]), nombre=str(juego[1]), precio=float(juego[2]), generos=str(juego[3]), tags=str(juego[4]), companias=str(juego[5]), fecha_lanzamiento=juego[6], sistema_operativo=str(juego[7]), calificacion=float(juego[8]))
        i+=1
    writer.commit()
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " juegos")   

def almacenar_juegos():
    f = urllib.request.urlopen("https://www.gog.com/en/games")

    lista =[]

    soup = BeautifulSoup(f, "lxml")

    datos = soup.find("div", class_="paginated-products-grid grid").find_all("product-tile")

    for juego in datos: 
            generos=[]
            tags=[]
            companias=[]
            url=juego.find("a")["href"]
            print(url)

            f2 = urllib.request.urlopen(url)
            soup2 = BeautifulSoup(f2, "lxml")
            #NOMBRE
            nombre = soup2.find("h1", class_="productcard-basics__title").text.strip()
            print(nombre)

            #PRECIO
            precio = soup2.find(attrs={"selenium-id": "ProductFinalPrice"}).text.strip()
            print(precio)

            #GENEROS
            genero = soup2.find("div", class_="details__content table__row-content").find_all("a")
            for i in genero:
                generos.append(i.text)
            print(generos)

            #TAGS
            tag = soup2.find(attrs={"selenium-id": "ProductTags"}).find("div",class_="details__content table__row-content").find_all("span", class_="details__link-text")
            for i in tag:
                tags.append(i.text)
            print(tags)    

            #COMPANIAS
            # Encuentra el siguiente hermano que contiene los enlaces a las compañías
            compania=soup2.find("div", class_="table__row details__rating details__row").next_sibling.next_sibling.find_all("a")
            for i in compania:
                companias.append(i.text)
            print(companias)

            #FECHALANZAMIENTO
            FechasinParseado=soup2.find("div", class_="table__row details__rating details__row").next_sibling.text.strip()
            match = re.search(r"(\d{4}-\d{2}-\d{2})", FechasinParseado)
            Fecha = match.group(1)
            print(Fecha)
            #WORKSON
            SistemaOperativo=soup2.find("div", class_="table__row details__rating details__row").find("div",class_="details__content table__row-content").text.strip()
            print(SistemaOperativo)
            #OverallRating
            if soup2.find("div",class_="rating productcard-rating__score") is not None:
                OverallRating=soup2.find("div",class_="rating productcard-rating__score").text.strip().split("/")[0]
            else:
                OverallRating=0.0

            print(OverallRating)
            print("-------------------------------------------------")
            lista.append((url,nombre,precio,generos,tags,companias,Fecha,SistemaOperativo,OverallRating))
    return lista


def cargar():
    almacenar_datos()
     

# Listar

def imprimir_lista(cursor):
    v = Toplevel()
    v.title("JUEGOS DE GOG")
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width = 150, yscrollcommand=sc.set)
    for row in cursor:
        lb.insert(END,row[0])
        lb.insert(END,"    Precio: "+ str(row[1]))
        lb.insert(END,"    Generos: "+ str(row[2]))
        lb.insert(END,"    Tags: "+ str(row[3]))
        lb.insert(END,"    Companyas: "+ str(row[4]))
        lb.insert(END,"    Fecha de lanzamiento: "+ str(row[5]))
        lb.insert(END,"    Sistemas Operativos: "+ str(row[6]))
        lb.insert(END,"    Calificacion: "+ str(row[7]))
        lb.insert(END,"")
    lb.pack(side=LEFT,fill=BOTH)
    sc.config(command = lb.yview)

def listar_juegos():
    # Abrimos el índice creado previamente
    ix = open_dir("Index")
    
    # Creamos un buscador para la búsqueda
    searcher = ix.searcher()
    
    # Usamos una consulta simple para recuperar todos los documentos (juegos)
    query = QueryParser("nombre", ix.schema).parse("*")  # '*' indica que buscamos todos los documentos
    results = searcher.search(query, limit=None)
    
    # Creamos una lista con los resultados para mostrar
    juegos_lista = []
    for result in results:
        juegos_lista.append((
            result['nombre'],
            result['precio'],
            result['generos'],
            result['tags'],
            result['companias'],
            result['fecha_lanzamiento'],
            result['sistema_operativo'],
            result['calificacion']
        ))
    
    searcher.close()
    
    # Llamamos a la función para imprimir la lista de juegos
    imprimir_lista(juegos_lista)
# Listar mejores

def listar_mejores_juegos():
    return 0


# DATOS
menudatos = Menu(menu, tearoff=0)
menudatos.add_command(label="Cargar", command=cargar)
menudatos.add_command(label="Salir", command=root.quit)
menu.add_cascade(label="Datos", menu=menudatos)

# LISTAR
menubuscar = Menu(menu, tearoff=0)
menubuscar.add_command(label="juegos", command=listar_juegos)
menubuscar.add_command(label="Mejores juegos", command=listar_mejores_juegos)
menu.add_cascade(label="Listar", menu=menubuscar)

root.config(menu=menu)
root.mainloop()