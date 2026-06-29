from django.shortcuts import render, get_object_or_404
from products.models import Category, Product, ProductUnit
from inventory.models import Inventory

def catalog_home(request):
    categories = Category.objects.filter(is_active=True)
    selected_category = request.GET.get('category', '')
    selected_manufacturer = request.GET.get('manufacturer', '')
    search_q = request.GET.get('q', '')

    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('units__inventory')

    if selected_category:
        products = products.filter(category__slug=selected_category)
    if selected_manufacturer:
        products = products.filter(manufacturer=selected_manufacturer)
    if search_q:
        products = products.filter(name_ar__icontains=search_q) | \
                   products.filter(name_en__icontains=search_q)

    manufacturers = Product.objects.filter(is_active=True)\
                           .exclude(manufacturer='')\
                           .values_list('manufacturer', flat=True)\
                           .distinct()

    context = {
        'products': products,
        'categories': categories,
        'manufacturers': manufacturers,
        'selected_category': selected_category,
        'selected_manufacturer': selected_manufacturer,
        'search_q': search_q,
    }

    # لو طلب HTMX يرجع partial بس
    if request.headers.get('HX-Request'):
        return render(request, 'catalog/partials/product_grid.html', context)

    return render(request, 'catalog/home.html', context)


def catalog_search(request):
    return catalog_home(request)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    units = product.units.prefetch_related('inventory').all()
    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'units': units,
    })
