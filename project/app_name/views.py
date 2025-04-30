# listar_juegos/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import sqlite3
from django.shortcuts import render
from .AII import almacenar_datos 
from django.views.decorators.csrf import csrf_exempt
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.query import Prefix
from whoosh.query import Regex, Term
from whoosh import sorting
def menu(request):
    # Puedes añadir lógica adicional aquí si necesitas mostrar algún dato especial
    return render(request, 'menu.html')

def listar_juegos(request):
    ix = open_dir("Index")
    juegos_dicts = []
    
    with ix.searcher() as searcher:
        # Obtener todos los documentos
        results = searcher.documents()
        
        for doc in results:
            juegos_dicts.append({
                'nombre': doc['nombre'],
                'precio': doc['precio'],
                'generos': doc['generos'].split(','),
                'tags': doc['tags'].split(','),
                'companias': doc['companias'].split(','),
                'fecha_lanzamiento': doc['fecha_lanzamiento'],
                'sistema_operativo': doc['sistema_operativo'],
                'calificacion': doc['calificacion'],
                'img': doc['img'],
            })

    return render(request, 'listar_juegos.html', {'juegos': juegos_dicts})


@csrf_exempt  # Añade este decorador si no estás enviando el CSRF token
@require_POST

def almacenar(request):
    try:
        almacenar_datos()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
def buscar(request):
    query = request.GET.get('q', '').strip()
    resultados = []
    
    if query:
        ix = open_dir("Index")
        
        with ix.searcher() as searcher:
            # Normalizamos la query a minúsculas para hacerla case-insensitive
            normalized_query = query.lower()
            
            # Creamos un filtro para nombres que empiecen exactamente con el query (case-insensitive)
            prefix_filter = Prefix("nombre_lower", normalized_query)
            results = searcher.search(prefix_filter, 
                                    limit=None, 
                                    sortedby=sorting.FieldFacet("nombre"))
            print(f"Resultados encontrados: {len(results)}")
            
            # Filtro adicional para asegurar que empieza exactamente (por si hay edge cases)
            exact_matches = []
            for hit in results:
                    exact_matches.append({
                        'nombre': hit['nombre'],
                        'precio': hit['precio'],
                        'generos': hit['generos'].split(','),
                        'tags': hit['tags'].split(','),
                        'companias': hit['companias'].split(','),
                        'fecha_lanzamiento': hit['fecha_lanzamiento'],
                        'sistema_operativo': hit['sistema_operativo'],
                        'calificacion': hit['calificacion'],
                        'img': hit['img'],
                    })
            
            resultados = exact_matches
    
    return render(request, 'buscar.html', {
        'resultados': resultados,
        'query': query
    })