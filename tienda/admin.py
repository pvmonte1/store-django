from django.contrib import admin
from .models import Producto, Variaciones, ReviewRating, ProductGallery
import admin_thumbnails


@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class AdminProducto(admin.ModelAdmin):
    prepoluted_fields = {'slug':('producto',)}
    list_display = ('producto','precio','stock','categoria','fecha_modificada','esta_disponible','slug')
    inlines = [ProductGalleryInline]


class AdminVariacion(admin.ModelAdmin):
    list_display = ('producto','categoria_variacion','valor_variacion','esta_activo')
    list_editable = ('esta_activo',)
    list_filter = ('producto','categoria_variacion','valor_variacion')
    
admin.site.register(Producto, AdminProducto)
admin.site.register(Variaciones, AdminVariacion)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)





