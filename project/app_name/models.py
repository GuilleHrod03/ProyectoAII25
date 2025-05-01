from django.db import models
from django.contrib.auth.models import User

class Juego(models.Model):
    url = models.CharField(max_length=200, unique=True)
    nombre = models.CharField(max_length=200)
    precio = models.FloatField()
    generos = models.CharField(max_length=500)
    tags = models.CharField(max_length=500)
    companias = models.CharField(max_length=500)
    fecha_lanzamiento = models.CharField(max_length=100, blank=True, null=True)
    sistema_operativo = models.CharField(max_length=100)
    calificacion = models.FloatField()
    img = models.URLField()
    
    def __str__(self):
        return self.nombre

class UserJuego(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    juego = models.ForeignKey(Juego, on_delete=models.CASCADE)
    play_time = models.FloatField(default=0)  # Tiempo jugado en horas
    rating = models.FloatField(null=True, blank=True)  # Puntuación de 1-5

    class Meta:
        unique_together = ('user', 'juego')

class UserTagJuego(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    juego = models.ForeignKey(Juego, on_delete=models.CASCADE)
    tag = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'juego', 'tag')