from django.contrib import messages
from .forms import ReviewForm
from django.http.response import HttpResponse
from django.shortcuts import redirect, render,  get_object_or_404
from .models import ProductGallery, Producto, ReviewRating
from categorias.models import Categoria
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q
from orders.models import OrderProduct



def tienda(request, categorias_slug=None):
    categorias = None
    productos = None

    if categorias_slug != None:
        categorias = get_object_or_404(Categoria, slug = categorias_slug)
        productos = Producto.objects.filter(categoria= categorias, esta_disponible= True)
        paginator = Paginator(productos, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        contar_producto = productos.count()
    else:
        productos = Producto.objects.all().filter(esta_disponible=True).order_by('id')
        paginator = Paginator(productos, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        contar_producto = productos.count()

    context = {
        'productos': paged_products,
        'contar_producto': contar_producto,
    }
    return render(request, 'tienda/tienda.html', context)



def detalles_producto(request, categorias_slug, productos_slug):
    try:
        solo_producto = Producto.objects.get(categoria__slug = categorias_slug, slug=productos_slug)
        en_carrito = CartItem.objects.filter(cart__cart_id= _cart_id(request), producto = solo_producto).exists()
       
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproducto = OrderProduct.objects.filter(user= request.user, producto_id= solo_producto.id).exists()
        except OrderProduct.DoesNotExist:
            orderproducto = None
    else:
        orderproducto = None

    # Get reviews ratings
    reviews = ReviewRating.objects.filter(producto_id= solo_producto.id, status = True)

    # Get Product Gallery
    product_gallery = ProductGallery.objects.filter(producto_id= solo_producto.id)

    context = {
        'solo_producto': solo_producto,
        'en_carrito'   : en_carrito,
        'orderproducto': orderproducto,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'tienda/detalles_producto.html', context)



def buscar(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            productos = Producto.objects.order_by('-fecha_creada').filter(Q(descripcion__icontains=keyword) | Q(producto__icontains=keyword))
            contar_producto = productos.count()
            
    context = {
        'productos': productos,
        'contar_producto': contar_producto,
    }    
    return render(request, 'tienda/tienda.html', context)


def submit_review(request, producto_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, producto__id=producto_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Gracias! Su revicion ha sido actualizada.')
            return redirect(url)
        
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.producto_id = producto_id
                data.user_id= request.user.id
                data.save()
                messages.success(request, 'Gracias! Su revicion ha sido sometida.')
                return redirect(url)


#

