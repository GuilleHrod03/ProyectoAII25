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
from whoosh.query import Regex, Term, NumericRange, Every, And
from whoosh import sorting
from whoosh.qparser import MultifieldParser
from whoosh import qparser

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


from whoosh.index import open_dir
from whoosh.query import Term, NumericRange, And, Every
from django.shortcuts import render

def filtrado(request):
    # Obtener parámetros de filtrado
    genero = request.GET.get('genero', '')
    compania = request.GET.get('compania', '')
    tag = request.GET.get('tag', '')
    sistema = request.GET.get('sistema', '')
    min_precio = request.GET.get('min_precio', '')
    max_precio = request.GET.get('max_precio', '')
    min_calificacion = request.GET.get('min_calificacion', '')

    # Diccionario de filtros activos
    filtros_activos = {
        'genero': genero,
        'compania': compania,
        'tag': tag,
        'sistema': sistema,
        'min_precio': min_precio,
        'max_precio': max_precio,
        'min_calificacion': min_calificacion,
    }

    # Verificar si hay algún filtro activo
    hay_filtros = any(filtros_activos.values())

    ix = open_dir("Index")
    with ix.searcher() as searcher:
        # Obtener y decodificar valores únicos para los dropdowns
        def decode_lexicon(lexicon_name):
            return [
                item.decode('utf-8') if isinstance(item, bytes) else item
                for item in searcher.lexicon(lexicon_name)
                if item  # Filtra valores vacíos
            ]

        generos = sorted(decode_lexicon('generos'))
        companias = sorted(decode_lexicon('companias'))
        tags = sorted(decode_lexicon('tags'))
        sistemas = sorted(decode_lexicon('sistema_operativo'))
        
        # Construir la consulta de filtrado
        query_parts = []
        
        if genero:
            query_parts.append(Term('generos', genero))
        if compania:
            query_parts.append(Term('companias', compania))
        if tag:
            query_parts.append(Term('tags', tag))
        if sistema:
            query_parts.append(Term('sistema_operativo', sistema))
        
        # Filtros numéricos
        if min_precio:
            try:
                query_parts.append(NumericRange('precio', float(min_precio), None))
            except ValueError:
                pass
        if max_precio:
            try:
                query_parts.append(NumericRange('precio', None, float(max_precio)))
            except ValueError:
                pass
        if min_calificacion:
            try:
                query_parts.append(NumericRange('calificacion', float(min_calificacion), None))
            except ValueError:
                pass
        
        # Combinar todas las condiciones con AND
        final_query = And(query_parts) if query_parts else Every()
        
        # Ejecutar la búsqueda
        resultados = []
        results = searcher.search(final_query, limit=None)
        
        for hit in results:
            # Función para decodificar campos separados por comas
            def decode_field(field_value):
                if not field_value:
                    return []
                return [
                    item.decode('utf-8') if isinstance(item, bytes) else item
                    for item in field_value.split(',')
                    if item  # Filtra valores vacíos
                ]

            resultados.append({
                'nombre': hit['nombre'].decode('utf-8') if isinstance(hit['nombre'], bytes) else hit['nombre'],
                'precio': hit['precio'],
                'generos': decode_field(hit['generos']),
                'tags': decode_field(hit['tags']),
                'companias': decode_field(hit['companias']),
                'fecha_lanzamiento': hit['fecha_lanzamiento'].decode('utf-8') if isinstance(hit['fecha_lanzamiento'], bytes) else hit['fecha_lanzamiento'],
                'sistema_operativo': hit['sistema_operativo'].decode('utf-8') if isinstance(hit['sistema_operativo'], bytes) else hit['sistema_operativo'],
                'calificacion': hit['calificacion'],
                'img': hit['img'].decode('utf-8') if isinstance(hit['img'], bytes) else hit['img'],
            })
    
    return render(request, 'filtrado.html', {
        'resultados': resultados,
        'generos': generos,
        'companias': companias,
        'tags': tags,
        'sistemas': sistemas,
        'filtros_activos': filtros_activos,
        'hay_filtros': hay_filtros
    })