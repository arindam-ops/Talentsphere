from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import Product


def product_list(request):
    products = Product.objects.filter(qty__gt=0)
    return render(request, 'students/product_list.html', {'products': products})


@login_required
def buy_product(request, product_id):
    if request.method != 'POST':
        return redirect('students:product_list')

    with transaction.atomic():
        product = get_object_or_404(Product.objects.select_for_update(), pk=product_id)
        if product.qty == 0:
            messages.error(request, 'This product is out of stock.')
        elif product.qty == 1:
            product.delete()
            messages.success(request, f'{product.product_name} purchased successfully.')
        else:
            product.qty -= 1
            product.save(update_fields=['qty'])
            messages.success(request, f'{product.product_name} purchased successfully.')

    return redirect('students:product_list')


def register(request):
    if request.user.is_authenticated:
        return redirect('students:product_list')

    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('students:product_list')

    return render(request, 'students/register.html', {'form': form})