from django.db import models
from django.db.models.deletion import CASCADE
from categorias.models import Categoria
from django.urls import reverse
from cuentas.models import Account

from django.db.models import Avg, Count





class Producto(models.Model):

    producto         = models.CharField(max_length=200, unique=True)
    slug             = models.SlugField(max_length=200, unique=True)
    descripcion      = models.TextField(max_length=500, blank= True)
    precio           = models.IntegerField()
    images           = models.ImageField(upload_to ='photos/products')
    stock            = models.IntegerField()
    esta_disponible  = models.BooleanField(default=True)
    categoria        = models.ForeignKey(Categoria, on_delete= models.CASCADE)
    fecha_creada     = models.DateTimeField(auto_now_add=True)
    fecha_modificada = models.DateTimeField(auto_now=True)

    def get_url (self):
        return reverse('detalles_producto', args=[self.categoria.slug, self.slug])

    def __str__(self):
        return self.producto

    def averageRating(self):
        reviews = ReviewRating.objects.filter(producto=self, status = True).aggregate(average = Avg('rating'))
        avg = 0
        if reviews['average']is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(producto=self, status = True).aggregate(count = Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count




class ManagerVariacion(models.Manager):
    def colors(self):
        return super(ManagerVariacion, self).filter(categoria_variacion='color', esta_activo=True)

    def sizes(self):
        return super(ManagerVariacion, self).filter(categoria_variacion='size', esta_activo = True)



escoger_variacion_categoria = (
    ('color', 'color'),
    ('size', 'size'),
)


class Variaciones(models.Model):
    producto            = models.ForeignKey(Producto, on_delete=models.CASCADE)
    categoria_variacion = models.CharField(max_length=100, choices= escoger_variacion_categoria)
    valor_variacion     = models.CharField(max_length=100)
    esta_activo         = models.BooleanField(default=True)
    fecha_creado        = models.DateTimeField(auto_now_add=True)

    objects = ManagerVariacion()

    def __str__(self):
        return self.valor_variacion




class ReviewRating(models.Model):
    producto     = models.ForeignKey(Producto, on_delete=models.CASCADE)
    user         = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject      = models.CharField(max_length=100, blank=True)
    review       = models.TextField(max_length=500, blank=True)
    rating       = models.FloatField()
    ip           = models.CharField(max_length=20, blank=True)
    status       = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__ (self):
        return self.subject 


class ProductGallery(models.Model):
    producto = models.ForeignKey(Producto, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to ='photos/products', max_length =255)

    def __str__(self):
        return self.producto.producto

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'

   




