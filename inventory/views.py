from django.shortcuts import render
from .models import Asset

# Assets
def asset_list(request):
    """
    Display a list of all assets with basic info.
    """
    assets = Asset.objects.all().order_by('name')
    
    context = {
        'assets': assets
    }
    return render(request, 'inventory/asset_list.html', context)

# Assignments
from django.shortcuts import render
from .models import Assignment

def assignment_list(request):
    """
    Display a list of all assignments, active and historical.
    """
    assignments = Assignment.objects.select_related('asset', 'entra_user').order_by('-assigned_date')
    
    context = {
        'assignments': assignments
    }
    return render(request, 'inventory/assignment_list.html', context)
