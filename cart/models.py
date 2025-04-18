from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from product.models import Product
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
import pytz
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver



class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    total_price = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)

    def __str__(self):
        return f"Cart for {self.user}"

    def update_totals(self):
        """Обновление итоговой суммы и подытога"""
        self.subtotal = sum(item.subtotal() for item in self.items.all())  # Сумма без скидок
        self.total_price = sum(item.total_price() for item in self.items.all())  # Сумма с учетом скидок
        self.save()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    isOrder = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        """Рассчитываем цену товара (с учетом скидки) перед сохранением"""
        if self.product.promotion is not None:
            self.price = self.product.promotion
        else:
            self.price = self.product.price

        super(CartItem, self).save(*args, **kwargs)

        self.cart.update_totals()

    def subtotal(self):

        return self.product.price * self.quantity

    def total_price(self):

        return self.price * self.quantity

    def __str__(self):
        return f"{self.user.first_name} {self.product.title}"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255)
    by_card = models.BooleanField(default=False)
    by_cash = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    application = models.BooleanField(default=False)  # Флаг успешного заказа
    ordered = models.BooleanField(default=False)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, null=True, blank=True)
    def save(self, *args, **kwargs):
        # Устанавливаем роль, если не указана
        if not self.role:
            self.role = self.user.role if self.user else 'customer'

        # Если заказ оформлен (оплачено наличными или картой), ставим application=True
        if self.by_card or self.by_cash:
            self.application = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ {self.id} – {self.address}"

