from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import Inventory


def inventory_list(request):
    inventory = Inventory.objects.select_related(
        'product_unit__product__category'
    ).all()
    return render(request, 'inventory/list.html', {'inventory': inventory})
