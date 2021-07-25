
from django.shortcuts import  render, redirect, get_object_or_404
from tienda.models import Producto, Variaciones
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, producto_id):
    current_user = request.user
    producto = Producto.objects.get(id= producto_id) #get the producto id
    #if user is authenticated

    if current_user.is_authenticated:
        variaciones_producto = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variacion = Variaciones.objects.get(producto=producto, categoria_variacion__iexact= key, valor_variacion__iexact = value)
                    variaciones_producto.append(variacion)
                except:
                    pass
    
        
        is_cart_item_exists = CartItem.objects.filter(producto = producto, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(producto=producto, user= current_user)
            ex_var_list = []
            id = []
            for item in cart_item :
                variaciones_existentes = item.variaciones.all()
                ex_var_list.append(list(variaciones_existentes))
                id.append(item.id)

        

            if variaciones_producto in ex_var_list:
                #increase cart item quantity
                index = ex_var_list.index(variaciones_producto)
                item_id = id[index]
                item = CartItem.objects.get(producto= producto, id=item_id)
                item.quantity += 1
                item.save()

            else:
               
                item = CartItem.objects.create(producto= producto, quantity = 1, user= current_user)
                if len(variaciones_producto)> 0:
                    item.variaciones.clear()
                    item.variaciones.add(*variaciones_producto)
                item.save()
               
        else:  
        
            cart_item = CartItem.objects.create(
                producto = producto,
                quantity = 1,
                user = current_user,

            )
        
            if len(variaciones_producto)> 0:
                cart_item.variaciones.clear()
                cart_item.variaciones.add(*variaciones_producto)
            cart_item.save()
    
        return redirect('cart')
    else:
    #if the user is not authenticated

        variaciones_producto = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variacion = Variaciones.objects.get(producto=producto, categoria_variacion__iexact= key, valor_variacion__iexact = value)
                    variaciones_producto.append(variacion)
                except:
                    pass
    
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))  #get the cartI present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(producto = producto, cart = cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(producto=producto, cart=cart)
            # existing_variations -> database
            # current variations -> variaciones_producto
            # item =_id -> database

            ex_var_list = []
            id = []
            for item in cart_item :
                variaciones_existentes = item.variaciones.all()
                ex_var_list.append(list(variaciones_existentes))
                id.append(item.id)

        

            if variaciones_producto in ex_var_list:
                # increase cart item quantity
                index = ex_var_list.index(variaciones_producto)
                item_id = id[index]
                item = CartItem.objects.get(producto= producto, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(producto= producto, quantity = 1, cart = cart)
                if len(variaciones_producto)> 0:
                    item.variaciones.clear()
                    item.variaciones.add(*variaciones_producto)
                item.save()
        else:  
            cart_item = CartItem.objects.create(
                producto = producto,
                quantity = 1,
                cart = cart,
            )
        
            if len(variaciones_producto)> 0:
                cart_item.variaciones.clear()
                cart_item.variaciones.add(*variaciones_producto)
            cart_item.save()
    
        return redirect('cart')


def remove_cart(request, producto_id, cart_item_id ):
    
    producto = get_object_or_404(Producto, id = producto_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(producto= producto, user= request.user, id= cart_item_id)
        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))
            cart_item = CartItem.objects.get(producto=producto, cart=cart, id= cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect ('cart')



def remove_cart_item(request, producto_id, cart_item_id):

    producto = get_object_or_404(Producto, id = producto_id)
    
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(producto= producto, user= request.user, id=cart_item_id)

    else:
        cart = Cart.objects.get(cart_id= _cart_id(request))
        cart_item = CartItem.objects.get(producto= producto, cart = cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_item=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items =  CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active= True)
        for cart_item in cart_items:
            total += (cart_item.producto.precio * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (7 * total)/100
        grand_total= total + tax 
    except ObjectDoesNotExist:
        pass #  just ignore

    context = {
             'total': total,
             'quantity': quantity,
             'cart_items': cart_items,
             'tax': tax,
             'grand_total': grand_total,

         }


    return render(request, 'tienda/cart.html', context)

@login_required(login_url='entrar')
def checkout(request,total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total=0
        if request.user.is_authenticated:
            cart_items =  CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active= True)
        for cart_item in cart_items:
            total += (cart_item.producto.precio * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (7 * total)/100
        grand_total= total + tax 
    except ObjectDoesNotExist:
        pass # just ignore

    context = {
             'total': total,
             'quantity': quantity,
             'cart_items': cart_items,
             'tax': tax,
             'grand_total': grand_total,

         }
    return render (request,'tienda/checkout.html', context)
      


