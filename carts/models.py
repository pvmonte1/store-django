from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from tienda.models import Producto, Variaciones
from cuentas.models import Account

class Cart(models.Model):
    cart_id= models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)


    def __str__(self):
        return self.cart_id


class CartItem (models.Model):
    user         = models.ForeignKey(Account, on_delete= models.CASCADE, null=True)
    producto     = models.ForeignKey(Producto, on_delete=models.CASCADE)
    variaciones  = models.ManyToManyField(Variaciones, blank= True)
    cart         = models.ForeignKey(Cart, on_delete=CASCADE, null =True)
    quantity     = models.IntegerField()
    is_active    = models.BooleanField(default=True)


    def sub_total(self):
        return self.producto.precio * self.quantity


    def __unicode__(self):
        return self.producto


