from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Asset, Assignment, EntraUser
from .forms import AssetForm, AssignmentForm, AssignmentEditForm
import msal
from django.conf import settings
from django.contrib.auth import login, logout as django_logout
from django.contrib.auth.models import User
import requests

# All assets page
def asset_list(request):
    """
    Display a list of all assets with basic info.
    """
    # Prepare options for filter checkboxes
    status_options = [
        Asset.STATUS_OPERATIONAL, 
        Asset.STATUS_MAINTENANCE,
        Asset.STATUS_DECOMMISSIONED, 
        Asset.STATUS_LOST,
        Asset.STATUS_PENDING, 
        Asset.STATUS_RESERVED
    ]
    category_options = Asset.objects.values_list('category', flat=True).distinct()
    brand_options = Asset.objects.values_list('brand', flat=True).distinct()
    location_options = Asset.objects.values_list('location', flat=True).distinct()

    # Get filter values from GET parameters (from submitted form)
    selected_statuses = request.GET.getlist('status')
    selected_categories = request.GET.getlist('category')
    selected_brands = request.GET.getlist('brand')
    selected_locations = request.GET.getlist('location')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Construct the query (adding filters (if any selected) consecutively)
    assets = Asset.objects.all().order_by('name')

    # Apply status filter
    if selected_statuses:
        assets = assets.filter(status__in=selected_statuses)
    
    # Apply category filter
    if selected_categories:
        assets = assets.filter(category__in=selected_categories)

    # Apply brand filter
    if selected_brands:
        assets = assets.filter(brand__in=selected_brands)

    # Apply location filter
    if selected_locations:
        assets = assets.filter(location__in=selected_locations)

    # Filter by purchase date range if provided
    if start_date:
        assets = assets.filter(purchase_date__gte=start_date)
    if end_date:
        assets = assets.filter(purchase_date__lte=end_date)

    # Get sort field from GET parameters, default to 'name'
    sort_field = request.GET.get('sort', 'name')

    # Apply sorting to the assets queryset
    assets = assets.order_by(sort_field)

    context = {
        'assets': assets,
        'status_options': status_options,
        'category_options': category_options,
        'brand_options': brand_options,
        'location_options': location_options,
        'selected_statuses': selected_statuses,
        'selected_categories': selected_categories,
        'selected_brands': selected_brands,
        'selected_locations': selected_locations,
        'start_date': start_date,
        'end_date': end_date,
        'sort_field': sort_field,
    }

    return render(request, 'inventory/asset_list.html', context)

# All assignments page
def assignment_list(request):
    """
    Display a list of all assignments, active and historical.
    """
    # Prepare options for assignment filters
    locations = Assignment.objects.values_list("location", flat=True).distinct()

    # Get filter values from GET parameters (from submitted form)
    status_filter = request.GET.get("status")
    location_filter = request.GET.getlist("location")
    assigned_start = request.GET.get("assigned_start")
    assigned_end = request.GET.get("assigned_end")
    returned_start = request.GET.get("returned_start")
    returned_end = request.GET.get("returned_end")

    # Construct the query (adding filters (if any selected) consecutively)
    assignments = Assignment.objects.select_related('asset', 'entra_user').order_by('-assigned_date')

    # Apply filters if provided
    if status_filter:
        if status_filter == "active":
            assignments = assignments.filter(returned_date__isnull=True)
        elif status_filter == "returned":
            assignments = assignments.filter(returned_date__isnull=False)

    if location_filter:
        assignments = assignments.filter(location__in=location_filter)

    if assigned_start:
        assignments = assignments.filter(assigned_date__gte=assigned_start)
    if assigned_end:
        assignments = assignments.filter(assigned_date__lte=assigned_end)

    if returned_start:
        assignments = assignments.filter(returned_date__gte=returned_start)
    if returned_end:
        assignments = assignments.filter(returned_date__lte=returned_end)
    
    # Get sort field from GET parameters, default to '-assigned_date' (newest first)
    sort_field = request.GET.get('sort', '-assigned_date')

    # Apply sorting
    assignments = assignments.order_by(sort_field)
    
    context = {
    'assignments': assignments,
    'locations': locations,
    'status_filter': status_filter,
    'location_filter': location_filter,
    'assigned_start': assigned_start,
    'assigned_end': assigned_end,
    'returned_start': returned_start,
    'returned_end': returned_end,
    'sort_field': sort_field,
    }

    return render(request, 'inventory/assignment_list.html', context)

# Single asset details & assignments page
def asset_details(request, asset_id):
    """
    Display details for a single asset, including current and past assignments.
    """
    asset = get_object_or_404(Asset, id=asset_id)
    active_assignment = asset.assignments.filter(returned_date__isnull=True).first()
    assignments = asset.assignments.select_related('entra_user').order_by('-assigned_date')

    # Get sort field from GET parameters, default to '-assigned_date' (newest first)
    sort_field = request.GET.get('sort', '-assigned_date')

    # Apply sorting
    assignments = assignments.order_by(sort_field)

    context = {
        'asset': asset,
        'assignments': assignments,
        'active_assignment': active_assignment,
        'sort_field': sort_field,
    }
    
    return render(request, 'inventory/asset_details.html', context)

# Single user details & assignments page
def user_assignments(request, user_id):
    """
    Display all assignments for a single user.
    """
    user = get_object_or_404(EntraUser, id=user_id)
    assignments = user.user_assignments.select_related('asset').order_by('-assigned_date')

    # Get sort field from GET parameters, default to '-assigned_date' (newest first)
    sort_field = request.GET.get('sort', '-assigned_date')

    # Apply sorting
    assignments = assignments.order_by(sort_field)

    context = {
        'user': user,
        'assignments': assignments,
        'sort_field': sort_field,
    }

    return render(request, 'inventory/user_assignments.html', context)

# All Entra ID users page
def user_list(request):
    """
    Display a read-only list of all Entra users.
    """
    # Prepare options for filters
    departments = EntraUser.objects.values_list('department', flat=True).distinct()

    # Get filter values from GET parameters
    department_filter = request.GET.getlist('department')
    is_active_filter = request.GET.get('is_active', 'all')

    # Construct the query (adding filters (if any selected) consecutively)
    users = EntraUser.objects.all()

    # Apply department filter
    if department_filter:
        users = users.filter(department__in=department_filter)

    # Apply is_active filter
    if is_active_filter == 'true':
        users = users.filter(is_active=True)
    elif is_active_filter == 'false':
        users = users.filter(is_active=False)
    
    # Get sort field from GET parameters, default to 'display_name'
    sort_field = request.GET.get('sort', 'display_name')

    # Apply sorting
    users = users.order_by(sort_field)

    context = {
        'users': users,
        'departments': departments,
        'department_filter': department_filter,
        'is_active_filter': is_active_filter,
        'sort_field': sort_field,
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

# Create assignment form page
def create_assignment(request):
    asset_id = request.GET.get('asset_id')
    
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('assignment_list')
    else:
        initial = {}
        if asset_id:
            initial['asset'] = asset_id
        form = AssignmentForm(initial=initial)
    
    return render(request, 'inventory/create_assignment.html', {'form': form})

# Edit an assignment
def edit_assignment(request, assignment_id):
    """
    Edit an existing assignment (limited fields for historical integrity).
    """
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.method == "POST":
        form = AssignmentEditForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            return redirect('assignment_list')
        
    else:
        form = AssignmentEditForm(instance=assignment)

    return render(request, 'inventory/create_assignment.html', {'form': form, 'edit': True})

# SSO login logic
def ms_login(request):
    # Create an MSAL Confidential Client
    msal_app = msal.ConfidentialClientApplication(
        client_id=settings.MICROSOFT_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}",
        client_credential=settings.MICROSOFT_CLIENT_SECRET,
    )

    # Build the auth URL
    auth_url = msal_app.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=settings.MICROSOFT_REDIRECT_URI
    )
    return redirect(auth_url)

# SSO Callback
def ms_callback(request):
    # Get the "code" Microsoft sends back
    code = request.GET.get("code", None)

    if not code:
        return render(request, "login_error.html", {"message": "No code returned from Microsoft."})

    # Create MSAL client
    msal_app = msal.ConfidentialClientApplication(
        client_id=settings.MICROSOFT_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}",
        client_credential=settings.MICROSOFT_CLIENT_SECRET,
    )

    # Exchange the code for tokens
    token_result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=["User.Read"],
        redirect_uri=settings.MICROSOFT_REDIRECT_URI,
    )

    if "access_token" not in token_result:
        return HttpResponse("Could not acquire token from Microsoft. Please try again.", status=400)

    # Use access token to get user profile from Microsoft Graph
    graph_response = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {token_result['access_token']}"}
    )

    user_data = graph_response.json()

    # Get email and name
    email = user_data.get("mail") or user_data.get("userPrincipalName")
    name = user_data.get("displayName")

    # Create or get Django user
    user, created = User.objects.get_or_create(username=email, defaults={"first_name": name})

    # Log the user in
    login(request, user)

    return redirect("/")

# SSO logout logic
def ms_logout(request):
    # Log out from Django
    django_logout(request)
    
    # Clear the session completely
    request.session.flush()
    
    # Redirect to Microsoft logout to clear SSO cookies
    ms_logout_url = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/logout?post_logout_redirect_uri=http://localhost:8000/login/"
    
    return redirect(ms_logout_url)

# Home/Dashboard page
def home(request):

    total_assets = Asset.objects.count()
    unassigned_operational = Asset.objects.filter(
        status='Operational'
    ).exclude(
        assignments__returned_date__isnull=True
    ).count()
    need_work = Asset.objects.filter(
        status__in=[Asset.STATUS_MAINTENANCE, Asset.STATUS_PENDING]
    ).count()
    
    context = {
        'total_assets': total_assets,
        'unassigned_operational': unassigned_operational,
        'need_work': need_work
    }

    return render(request, 'inventory/home.html', context)

# Delete asset confirmation page
def asset_delete(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)

    if request.method == "POST":
        asset.delete()
        return redirect('asset_list')

    return render(request, 'inventory/asset_confirm_delete.html', {'asset': asset})
