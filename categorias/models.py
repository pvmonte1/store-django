from django.db import models
from django.urls import reverse


class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=50, unique=True)
    slug             = models.SlugField(max_length=100, unique=True)
    descripcion      = models.TextField(max_length=255, blank= True)
    imagen_cat       = models.ImageField(upload_to='photos/categorias', blank= True)

    class Meta:
        verbose_name ='Categoria'
        verbose_name_plural ='categorias'

    def get_url(self):
            return reverse('productos_por_categorias', args=[self.slug])
        

    def __str__(self):
        return self.nombre_categoria


