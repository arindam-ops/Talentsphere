from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    product_name = models.CharField(max_length=150)
    product_no = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    qty = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['product_name']

    def __str__(self):
        return f'{self.product_name} ({self.product_no})'