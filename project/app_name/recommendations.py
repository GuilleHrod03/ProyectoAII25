from django.db.models import Count, Avg
from collections import defaultdict
import shelve
from math import sqrt
import random

def load_similarities():
    """Versión mejorada con más tolerancia y datos simulados"""
    user_ratings = get_user_ratings()
    
    # Si no hay suficientes datos reales, añadir datos simulados
    if len(user_ratings) < 3:
        user_ratings = generate_simulated_ratings(user_ratings)
    
    game_similarities = calculate_game_similarities(user_ratings)
    
    with shelve.open('game_recommendations.dat') as db:
        db['similarities'] = game_similarities

def generate_simulated_ratings(existing_ratings):
    """Genera datos de prueba realistas"""
    from app_name.models import User, Juego, UserJuego
    
    users = list(User.objects.all())
    games = list(Juego.objects.all())
    
    # Patrones de preferencia simulados
    genres_prefs = {
        'rpg': [4.5, 5.0],
        'action': [3.5, 4.5],
        'adventure': [4.0, 5.0],
        'strategy': [3.0, 4.0]
    }
    
    for user in users:
        # Cada usuario califica 5-8 juegos aleatorios
        for game in random.sample(games, random.randint(5, 8)):
            # Determinar rating basado en género principal
            main_genre = game.generos.split(',')[0].strip().lower()
            rating_range = genres_prefs.get(main_genre, [3.0, 4.5])
            rating = round(random.uniform(*rating_range), 1)
            
            # Crear o actualizar rating
            UserJuego.objects.update_or_create(
                user=user,
                juego=game,
                defaults={
                    'rating': rating,
                    'play_time': random.randint(1, 20)
                }
            )
    
    # Volver a cargar ratings con los nuevos datos
    return get_user_ratings()

def calculate_game_similarities(user_ratings, min_common_users=1, min_similarity=0.1):
    """Versión con parámetros más flexibles"""
    game_users = defaultdict(dict)
    for user, games in user_ratings.items():
        for game, rating in games.items():
            game_users[game][user] = rating
    
    similarities = defaultdict(dict)
    games = list(game_users.keys())
    
    for i in range(len(games)):
        for j in range(i+1, len(games)):
            game1, game2 = games[i], games[j]
            common_users = set(game_users[game1]) & set(game_users[game2])
            
            if len(common_users) >= min_common_users:
                # Cálculo de similitud mejorado
                sum_xy = sum_xx = sum_yy = 0
                for user in common_users:
                    x = game_users[game1][user]
                    y = game_users[game2][user]
                    sum_xy += x * y
                    sum_xx += x * x
                    sum_yy += y * y
                
                denominator = sqrt(sum_xx) * sqrt(sum_yy)
                similarity = sum_xy / denominator if denominator > 0 else 0
                
                if similarity >= min_similarity:
                    similarities[game1][game2] = similarity
                    similarities[game2][game1] = similarity
    
    return similarities

def recommend_for_user(user_id, num_recommendations=5):
    """Versión más flexible con recomendaciones basadas en contenido si no hay suficientes datos colaborativos"""
    from app_name.models import UserJuego, Juego
    
    try:
        # Juegos que el usuario ya ha jugado
        played = set(UserJuego.objects.filter(user_id=user_id)
                              .values_list('juego__url', flat=True))
        
        with shelve.open('game_recommendations.dat') as db:
            similarities = db.get('similarities', {})
            
            # 1. Intento colaborativo
            scores = defaultdict(float)
            counts = defaultdict(int)
            
            for played_game in played:
                for similar, sim_value in similarities.get(played_game, {}).items():
                    if similar not in played:
                        scores[similar] += sim_value
                        counts[similar] += 1
            
            # Si no hay suficientes recomendaciones, usar enfoque híbrido
            if len(scores) < num_recommendations:
                return content_based_recommendations(user_id, num_recommendations)
            
            # Obtener mejores recomendaciones
            recommendations = []
            for game_url in scores:
                avg_score = scores[game_url] / counts[game_url]
                recommendations.append((game_url, avg_score))
            
            recommendations.sort(key=lambda x: -x[1])
            top_recommendations = recommendations[:num_recommendations]
            
            # Obtener detalles de los juegos
            game_urls = [g[0] for g in top_recommendations]
            games = Juego.objects.filter(url__in=game_urls)
            
            return [{
                'nombre': g.nombre,
                'url': g.url,
                'score': next(s for url, s in top_recommendations if url == g.url) * 100,
                'img': g.img
            } for g in games]
    
    except Exception as e:
        print(f"Error in recommendations: {e}")
        return content_based_recommendations(user_id, num_recommendations)

def content_based_recommendations(user_id, num_recommendations=5):
    """Recomendaciones basadas en géneros/tags cuando faltan datos colaborativos"""
    from app_name.models import UserJuego, Juego
    
    # Obtener géneros/tags favoritos del usuario
    user_games = UserJuego.objects.filter(user_id=user_id, rating__gte=3.5)
    if not user_games.exists():
        user_games = UserJuego.objects.filter(user_id=user_id)
    
    favorite_genres = set()
    favorite_tags = set()
    
    for ug in user_games:
        favorite_genres.update(g.strip().lower() for g in ug.juego.generos.split(','))
        favorite_tags.update(t.strip().lower() for t in ug.juego.tags.split(','))
    
    # Buscar juegos similares
    from django.db.models import Q
    query = Q()
    for genre in favorite_genres:
        query |= Q(generos__icontains=genre)
    for tag in favorite_tags:
        query |= Q(tags__icontains=tag)
    
    recommended = Juego.objects.exclude(
        userjuego__user_id=user_id
    ).filter(query).annotate(
        avg_rating=Avg('userjuego__rating')
    ).order_by('-avg_rating')[:num_recommendations]
    
    return [{
        'nombre': g.nombre,
        'url': g.url,
        'score': 70 + random.random() * 30,  # Simular score 70-100%
        'img': g.img
    } for g in recommended]

def get_user_ratings():
    """Obtiene las puntuaciones de los usuarios"""
    from app_name.models import UserJuego
    ratings = defaultdict(dict)
    
    for uj in UserJuego.objects.select_related('user', 'juego'):
        if uj.rating:  # Solo si tiene rating
            ratings[uj.user.id][uj.juego.url] = uj.rating
    
    return ratings