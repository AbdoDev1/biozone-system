from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Category, Product


def category_list(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'products/category_list.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = category.products.filter(is_active=True).prefetch_related('units')
    return render(request, 'products/category_detail.html', {
        'category': category,
        'products': products,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    units = product.units.all()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'units': units,
    })
