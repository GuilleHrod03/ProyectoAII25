# listar_juegos/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import sqlite3
from django.shortcuts import render
from .AII import almacenar_datos 
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Añade este decorador si no estás enviando el CSRF token
@require_POST


def listar_juegos(request):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, precio, generos, tags, companias, fecha_lanzamiento, sistema_operativo, calificacion FROM juegos")
    juegos = cursor.fetchall()
    conn.close()

    juegos_dicts = []
    for juego in juegos:
        juegos_dicts.append({
            'nombre': juego[0],
            'precio': juego[1],
            'generos': juego[2].split(','),
            'tags': juego[3].split(','),
            'companias': juego[4].split(','),
            'fecha_lanzamiento': juego[5],
            'sistema_operativo': juego[6],
            'calificacion': juego[7],
        })

    return render(request, 'listar_juegos.html', {'juegos': juegos_dicts})


def almacenar(request):
    try:
        almacenar_datos()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def buscar(request):
    query = request.GET.get('q', '')
    resultados = []
    
    if query:
        conn = sqlite3.connect("db.sqlite3")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nombre, precio, generos, tags, companias, fecha_lanzamiento, sistema_operativo, calificacion 
            FROM juegos 
            WHERE nombre LIKE ? OR generos LIKE ? OR tags LIKE ? OR companias LIKE ?
        """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        
        resultados = cursor.fetchall()
        conn.close()
        
        # Convertir a diccionarios como en listar_juegos
        resultados = [{
            'nombre': juego[0],
            'precio': juego[1],
            'generos': juego[2].split(','),
            'tags': juego[3].split(','),
            'companias': juego[4].split(','),
            'fecha_lanzamiento': juego[5],
            'sistema_operativo': juego[6],
            'calificacion': juego[7],
        } for juego in resultados]
    
    return render(request, 'buscar.html', {
        'resultados': resultados,
        'query': query
    })