from django.shortcuts import render, get_object_or_404, redirect
from .models import Asset, Assignment, EntraUser
from .forms import AssetForm

# All assets page
def asset_list(request):
    """
    Display a list of all assets with basic info.
    """
    assets = Asset.objects.all().order_by('name')
    
    context = {
        'assets': assets
    }
    return render(request, 'inventory/asset_list.html', context)

# All assignments page
def assignment_list(request):
    """
    Display a list of all assignments, active and historical.
    """
    assignments = Assignment.objects.select_related('asset', 'entra_user').order_by('-assigned_date')
    
    context = {
        'assignments': assignments
    }
    return render(request, 'inventory/assignment_list.html', context)

# Single asset detail page
def asset_details(request, asset_id):
    """
    Display details for a single asset, including current and past assignments.
    """
    asset = get_object_or_404(Asset, id=asset_id)
    assignments = asset.assignments.select_related('entra_user').order_by('-assigned_date')

    context = {
        'asset': asset,
        'assignments': assignments
    }
    return render(request, 'inventory/asset_details.html', context)

# Single user details & assignments
def user_assignments(request, user_id):
    """
    Display all assignments for a single user.
    """
    user = get_object_or_404(EntraUser, id=user_id)
    assignments = user.assignments.select_related('asset').order_by('-assigned_date')

    context = {
        'user': user,
        'assignments': assignments
    }
    return render(request, 'inventory/user_assignments.html', context)

# All Entra ID users page
def user_list(request):
    """
    Display a read-only list of all Entra users.
    """
    users = EntraUser.objects.all().order_by('display_name')
    
    context = {
        'users': users
    }
    return render(request, 'inventory/user_list.html', context)

# Add an asset form page
def create_asset(request):
    """
    Handles the creation of a new Asset.
    
    GET: Displays an empty AssetForm.
    POST: Validates and saves the form, then redirects to the asset list.
    """
    if request.method == "POST":

        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('asset_list')
        
    else:
        form = AssetForm()
    
    return render(request, 'inventory/asset_form.html', {'form': form})

# Edit an asset form page
def edit_asset(request, asset_id):
    """
    Edit an existing asset.
    """
    asset = get_object_or_404(Asset, id=asset_id)

    if request.method == "POST":

        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            return redirect('asset_details', asset_id=asset.id)
        
    else:
        form = AssetForm(instance=asset)
    
    return render(request, 'inventory/asset_form.html', {'form': form, 'edit': True})
