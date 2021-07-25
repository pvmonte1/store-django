from django.shortcuts import get_object_or_404, redirect, render
from .forms import FormaRegistracion, UserForm, UserProfileForm
from .models import Account, UserProfile
from orders.models import Order, OrderProduct
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# Verification Email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests


def registrate(request):
    if request.method == 'POST':
        form = FormaRegistracion(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name = first_name, last_name= last_name, email = email, username = username, password=password)
            user.phone = phone
            user.save()

            # Create User Profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture ='photos/media/default/avatar.png'
            profile.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = ' Por favor active su cuenta'
            message = render_to_string('cuentas/verificacion_cuentas_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            #messages.success(request, 'Gracias por registrace con nosotros. Le hemos enviado un enlace de activacion a su correo.')
            return redirect('/cuentas/entrar/?command=verification&email='+email)

    else:
        form = FormaRegistracion()
    
    context = {
        'form': form,
    }
    return render (request , 'cuentas/registrate.html', context)

def entrar(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    variaciones_producto = []


                # Getting Variaciones de producto by Cart ID
                    for item in cart_item:
                        variacion = item.variaciones.all()
                        variaciones_producto.append(list(variacion))
                        
                        #get the cart items from the user to access his product variationes
                    cart_item = CartItem.objects.filter( user= user)
                    ex_var_list = []
                    id = []
                    for item in cart_item :
                        variaciones_existentes = item.variaciones.all()
                        ex_var_list.append(list(variaciones_existentes))
                        id.append(item.id)    

                    for pr in variaciones_producto:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass

            auth.login(request, user)
            messages.success(request, 'Usted a entrado a la Cuenta')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
               
            except:
               return redirect('dashboard')
        else:
            messages.error(request, 'Credenciales Invalidas')
            return redirect('entrar')
    return render(request, 'cuentas/entrar.html')


@login_required(login_url='entrar')
def salir(request):
    auth.logout(request)
    messages.success(request,'Usted a salido de la Cuenta')
    return redirect('entrar')  

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Felicitaciones ! Su cuenta esta activa.')
        return redirect('entrar')
    else:
        messages.error(request, 'Enlace Invalido')
        return redirect('registrate')


@login_required(login_url = 'entrar')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered = True)
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user_id=request.user.id)

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    
    return render(request,'cuentas/dashboard.html', context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            #Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Renueve su Contarseña'
            message = render_to_string('cuentas/reset_password_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request,'Un enlace a sido enviado a su correo para recuperar Contraseña.')
            return redirect('entrar')


        else:
            messages.error(request, 'Esta cuenta no Existe!')
            return redirect('forgotPassword')
    return render(request, 'cuentas/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request, 'Favor escoger Contraseña')
        return redirect ('resetPassword')

    else:
        messages.error(request, 'este enlace esta expirado!')
        return redirect('entrar')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password== confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'La contraseña a sido cambiada satisfactoriamente !')
            return redirect('entrar')

        else:
            messages.error(request,'La contraseña no es igual')
            return redirect('resetPassword')
    else:
        return render(request, 'cuentas/resetPassword.html')

@login_required(login_url='entrar')
def mis_ordenes(request):
    orders = Order.objects.filter(user=request.user, is_ordered = True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'cuentas/mis_ordenes.html', context)

def editar_perfil(request):
    userprofile = get_object_or_404(UserProfile, user= request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance= request.user)
        profile_form  = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Su perfil a sido actualizado')
            return redirect('editar_perfil')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance= userprofile)
    context = {
        'user_form': user_form,
        'profile_form' : profile_form,
        'userprofile': userprofile,
    }

    return render(request, 'cuentas/editar_perfil.html', context)

@login_required(login_url='entrar')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact = request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                 # auth.logout(request)
                messages.success(request,'Contraseña actualizada correctamente.')
                return redirect('change_password')
            else:
                messages.error(request, 'Favor entrar la contraseña Existente.')
                return redirect('change_password')
        else:
            messages.error(request, 'La contraseña nueva NO coincide!')
            return redirect('change_password')

    return render(request, 'cuentas/change_password.html')

@login_required(login_url='entrar')
def order_detail(request, order_id):  
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order= Order.objects.get(order_number= order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.producto.precio * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }

    return render(request, 'cuentas/order_detail.html', context) 






        

