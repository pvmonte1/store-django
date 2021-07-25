
from django.urls import path
from .import views

urlpatterns = [
    path('', views.tienda, name='tienda'),
    path('categoria/<slug:categorias_slug>/', views.tienda, name='productos_por_categorias'),
    path('categoria/<slug:categorias_slug>/<slug:productos_slug>/', views.detalles_producto, name='detalles_producto'),
    path('buscar/', views.buscar, name='buscar'),
    path('submit_review/<int:producto_id>/', views.submit_review, name='submit_review'),
]