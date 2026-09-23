from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_no', 'price', 'qty')
    list_editable = ('price', 'qty')
    search_fields = ('product_name', 'product_no')