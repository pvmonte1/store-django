from django.shortcuts import render
from tienda.models import Producto, ReviewRating

def home(request):
    productos = Producto.objects.all().filter(esta_disponible=True).order_by('-fecha_creada')

    for producto in productos :
        reviews = ReviewRating.objects.filter(producto_id= producto.id, status = True)

    context = {
        'productos': productos,
        'reviews': reviews,
    }
    return render(request, 'home.html', context)
