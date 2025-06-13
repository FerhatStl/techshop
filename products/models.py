from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings

class Category(models.Model):
        name = models.CharField(max_length=255, unique=True)
        image = models.ImageField(upload_to='categories/', null=True, blank=True)
        description = models.TextField(null=True, blank=True)

        def __str__(self):
            return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    image_url = models.ImageField(upload_to='products/', null=True, blank=True)
    category_id = models.ForeignKey(
        'Category', 
        on_delete=models.CASCADE, 
        null=False, 
        blank=False, 
        related_name='products',
        default=1
    )


class CustomUser(AbstractUser):
    # Add any custom fields here if needed
    cart = models.JSONField(default=list, blank=True)


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.country}"


class Card(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cards')
    card_number = models.CharField(max_length=16)
    cardholder_name = models.CharField(max_length=255)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=4)

    def __str__(self):
        return f"Card ending in {self.card_number[-4:]}"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')
    card_holder = models.CharField(max_length=255, null=True, blank=True)
    card_last4 = models.CharField(max_length=4, null=True, blank=True)
    address_street = models.CharField(max_length=255, null=True, blank=True)
    address_city = models.CharField(max_length=255, null=True, blank=True)
    address_state = models.CharField(max_length=255, null=True, blank=True)
    address_zip = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"




