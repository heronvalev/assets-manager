from django.shortcuts import render
from .models import Asset

def asset_list(request):
    """
    Display a list of all assets with basic info.
    """
    assets = Asset.objects.all().order_by('name')
    
    context = {
        'assets': assets
    }
    return render(request, 'inventory/asset_list.html', context)
