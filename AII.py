import urllib.request 
from tkinter import Tk, Button, Toplevel, Label, END, LEFT, BOTH, RIGHT, Listbox, Menu, Entry, Spinbox, Scrollbar, messagebox
from bs4 import BeautifulSoup
import sqlite3

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context 
#Para evitar problemas con BeautifulSoup

conn = sqlite3.connect('consolas.db')

root = Tk()
menu = Menu(root)




# Cargar
def crear_esquema():
    return 0


def almacenar_consolas():
    f = urllib.request.urlopen("https://es.wikipedia.org/wiki/Anexo:Consolas_de_Nintendo")

    soup = BeautifulSoup(f, "lxml")

    datos = soup.find("table", class_="wikitable").find("tbody").find_all("tr")
    consolas = []

    flag = 0

    for consola in datos:
        if flag == 0:
            flag += 1
        else:
            nombre = consola.find("td").a.text
            años = consola.find("td").find_next_sibling().find_next_sibling().text.strip()
            unidades = consola.find("td").find_next_sibling().find_next_sibling().find_next_sibling().text.strip()
            if "millones" in unidades:
                unidades = float(unidades.split(" ")[0].replace(',', '.')) * 1000000
            elif "mil" in unidades:
                unidades = float(unidades.split(" ")[0].replace(',', '.')) * 1000
            elif "?" in unidades:
                unidades = 0
                
            url = "https://es.wikipedia.org/" + consola.find("td").a["href"]
            f2 = urllib.request.urlopen(url)
            soup2 = BeautifulSoup(f2, "lxml")
            
            tabla = soup2.find("table", class_="infobox").find("tbody")
            tipo = tabla.find("th", string="Tipo").find_next("td").text.strip()

            if nombre == "Nintendo Switch":
                generacion1 = tabla.find("th", string="Generación").find_next("td").a.text
                generacion2 = tabla.find("th", string="Generación").find_next("td").a.find_next_sibling().text
                generacion = f"{generacion1}/{generacion2}"
            elif tabla.find("th", string="Generación"):
                generacion = tabla.find("th", string="Generación").find_next("td").text.strip()
            else:
                generacion = "Desconocido"
            desarrollador = tabla.find("th", string="Desarrollador").find_next("td").text.strip()
            conn.execute("""INSERT INTO CONSOLAS (NOMBRE, ANYOS, UNIDADES, TIPO, GENERACION, DESARROLLADOR) VALUES (?,?,?,?,?,?)""",
                     (nombre,años,unidades,tipo,generacion,desarrollador))
            conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM CONSOLAS")
    messagebox.showinfo( "Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")

def cargar():

    almacenar_consolas()
     

# Listar
def listar_consolas():
    conn = sqlite3.connect("consolas.db")
    cursor = conn.cursor()
    # mostrar todos los datos en una ventana con listbox y scrollbar
    nueva_ventana = Toplevel()
    nueva_ventana.title("Listado de consolas")
    cursor.execute("SELECT * FROM CONSOLAS")

    lb = Listbox(nueva_ventana)
    for row in cursor:
        lb.insert(END, f"Nombre: {row[0]}")
        lb.insert(END, f"Años: {row[1]}")
        lb.insert(END, f"Unidades: {row[2]}")
        lb.insert(END, f"Tipo: {row[3]}")
        lb.insert(END, f"Generacion: {row[4]}")
        lb.insert(END, f"Desarrollador: {row[5]}")
        lb.insert(END, "")

    lb.pack(side=LEFT, fill=BOTH, expand=True)

    # Scrollbar
    # Creación scrollbar
    sc = Scrollbar(nueva_ventana)
    sc.pack(side = RIGHT, fill = BOTH) 

    # Configuración del scrollbar, sobre lb y su comando ("lb.yview")
    lb.config(yscrollcommand = sc.set) 
    sc.config(command = lb.yview)

# Listar mejores
def listar_mejores_consolas():
    conn = sqlite3.connect("consolas.db")
    cursor = conn.cursor()
    # mostrar todos los datos en una ventana con listbox y scrollbar
    nueva_ventana = Toplevel()
    nueva_ventana.title("Listado de las mejores 5 consolas")
    cursor.execute("SELECT * "
                   "FROM CONSOLAS "
                   "ORDER BY UNIDADES DESC "
                   "LIMIT 5;")

    lb = Listbox(nueva_ventana)
    for row in cursor:
        lb.insert(END, f"Nombre: {row[0]}")
        lb.insert(END, f"Años: {row[1]}")
        lb.insert(END, f"Unidades: {row[2]}")
        lb.insert(END, f"Tipo: {row[3]}")
        lb.insert(END, f"Generacion: {row[4]}")
        lb.insert(END, f"Desarrollador: {row[5]}")

        lb.insert(END, "")

    lb.pack(side=LEFT, fill=BOTH, expand=True)

    # Scrollbar
    # Creación scrollbar
    sc = Scrollbar(nueva_ventana)
    sc.pack(side = RIGHT, fill = BOTH) 

    # Configuración del scrollbar, sobre lb y su comando ("lb.yview")
    lb.config(yscrollcommand = sc.set) 
    sc.config(command = lb.yview)

#Buscar generacion
def mostrar_seleccion_generacion(event, entry):
    cursor = conn.cursor()
    nueva_ventana = Toplevel()
    
    generacion = entry.get()
    cursor.execute ("SELECT * FROM CONSOLAS WHERE GENERACION LIKE ?", (generacion,))

    lb = Listbox(nueva_ventana)

    lb.insert(END, f"Generacion {generacion}")
    lb.insert(END, "----------------------------")
    for row in cursor:
        lb.insert(END, f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}")
    lb.insert(END, "")

    lb.pack(side=LEFT, fill=BOTH, expand=True)

    # Scrollbar
    # Creación scrollbar
    sc = Scrollbar(nueva_ventana)
    sc.pack(side = RIGHT, fill = BOTH) 

    # Configuración del scrollbar, sobre lb y su comando ("lb.yview")
    lb.config(yscrollcommand = sc.set) 
    sc.config(command = lb.yview) 

def buscar_generacion():
    nueva_ventana = Toplevel()
    nueva_ventana.title("Busqueda por generacion")
    
    Label(nueva_ventana, text="Seleccione una generacion").pack()
    cursor = conn.execute("""SELECT DISTINCT GENERACION FROM CONSOLAS""")
    valores=[i[0] for i in cursor]
    
    lb = Label(nueva_ventana, text="Seleccione la generacion: ")
    lb.pack(side = LEFT)
    en = Spinbox(nueva_ventana,values=valores,state="readonly")
    en.bind("<Return>", lambda event: mostrar_seleccion_generacion(event, en))
    en.pack(side = LEFT)

# Buscar tipo
def mostrar_seleccion_tipo(event, entry):
    cursor = conn.cursor()
    nueva_ventana = Toplevel()
    
    generacion = entry.get()
    cursor.execute ("SELECT * FROM CONSOLAS WHERE TIPO LIKE ?", (generacion,))

    lb = Listbox(nueva_ventana)

    lb.insert(END, f"TIPO: {generacion}")
    lb.insert(END, "----------------------------")
    for row in cursor:
        lb.insert(END, f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}")
    lb.insert(END, "")

    lb.pack(side=LEFT, fill=BOTH, expand=True)

    # Scrollbar
    # Creación scrollbar
    sc = Scrollbar(nueva_ventana)
    sc.pack(side = RIGHT, fill = BOTH) 

    # Configuración del scrollbar, sobre lb y su comando ("lb.yview")
    lb.config(yscrollcommand = sc.set) 
    sc.config(command = lb.yview) 

def buscar_tipo():
    nueva_ventana = Toplevel()
    nueva_ventana.title("Busqueda por generacion")
    
    Label(nueva_ventana, text="Seleccione una generacion").pack()
    cursor = conn.execute("""SELECT DISTINCT TIPO FROM CONSOLAS""")
    valores=[i[0] for i in cursor]
    
    lb = Label(nueva_ventana, text="Seleccione la tipo: ")
    lb.pack(side = LEFT)
    en = Spinbox(nueva_ventana,values=valores,state="readonly")
    en.bind("<Return>", lambda event: mostrar_seleccion_tipo(event, en))
    en.pack(side = LEFT)

# DATOS
menudatos = Menu(menu, tearoff=0)
menudatos.add_command(label="Cargar", command=cargar)
menudatos.add_command(label="Salir", command=root.quit)
menu.add_cascade(label="Datos", menu=menudatos)

# LISTAR
menubuscar = Menu(menu, tearoff=0)
menubuscar.add_command(label="Consolas", command=listar_consolas)
menubuscar.add_command(label="Mejores consolas", command=listar_mejores_consolas)
menu.add_cascade(label="Listar", menu=menubuscar)

# BUSCAR
menubuscar = Menu(menu, tearoff=0)
menubuscar.add_command(label="Por generación", command=buscar_generacion)
menubuscar.add_command(label="Por tipo", command=buscar_tipo)
menu.add_cascade(label="Buscar", menu=menubuscar)

root.config(menu=menu)
root.mainloop()