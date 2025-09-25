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
    active_assignment = asset.assignments.filter(returned_date__isnull=True).first()
    assignments = asset.assignments.select_related('entra_user').order_by('-assigned_date')

    context = {
        'asset': asset,
        'assignments': assignments,
        'active_assignment': active_assignment
    }
    
    return render(request, 'inventory/asset_details.html', context)

# Single user details & assignments
def user_assignments(request, user_id):
    """
    Display all assignments for a single user.
    """
    user = get_object_or_404(EntraUser, id=user_id)
    assignments = user.user_assignments.select_related('asset').order_by('-assigned_date')

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

def ms_logout(request):
    # Log out from Django
    django_logout(request)
    
    # Clear the session completely
    request.session.flush()
    
    # Redirect to Microsoft logout to clear SSO cookies
    ms_logout_url = f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT_ID}/oauth2/v2.0/logout?post_logout_redirect_uri=http://localhost:8000/login/"
    
    return redirect(ms_logout_url)