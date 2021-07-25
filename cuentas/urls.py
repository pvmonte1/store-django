
from django.urls import path
from .import views

urlpatterns = [
    path('registrate/', views.registrate, name ='registrate'),
    path('entrar/', views.entrar, name ='entrar'),
    path('salir/', views.salir, name ='salir'),
    path('dashboard/', views.dashboard, name ='dashboard'),
    path('', views.dashboard, name ='dashboard'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
   
    path('mis_ordenes/', views.mis_ordenes, name='mis_ordenes'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
]
