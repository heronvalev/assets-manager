from django.db import models
from django.utils import timezone

# Entra Users table to sync with Microsoft Graph API
class EntraUser(models.Model):
    entra_user_id = models.CharField(max_length=36, unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    upn = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    department = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.display_name} ({self.upn})"
    
# Assets table for all assets/devices    
class Asset(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, default="active")
    location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"
    
    def is_assigned(self):
        """
        Returns True if the asset is currently assigned to a user 
        (it has at least one Assignment without a returned_date).
        Otherwise returns False.
        """
        return self.assignments.filter(returned_date__isnull=True).exists()
    
    def get_current_location(self):
        """
        Returns the asset's current location:
        - If the asset is assigned, returns the location from the active Assignment.
        - If unassigned, returns the location stored in the Asset table.
        """
        active_assignment = self.assignments.filter(returned_date__isnull=True).first()

        if active_assignment:
            return active_assignment.location
        
        return self.location
    
    def get_current_user_upn(self):
        """
        Returns the UPN of the user currently assigned to this asset, or None if unassigned.
        """
        active_assignment = self.assignments.filter(returned_date__isnull=True).first()
        if active_assignment:
            return active_assignment.entra_user.upn if active_assignment.entra_user else "Team/Room"
        return "Available"
        
# Assignments table to track current and historical asset assignment    
class Assignment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="assignments")
    entra_user = models.ForeignKey(EntraUser, null=True, blank=True, on_delete=models.SET_NULL, related_name="assignments")
    assigned_date = models.DateField(default=timezone.now)
    returned_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    assignment_reason = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.asset.name} -> {self.entra_user.display_name if self.entra_user else 'Unassigned'}"

    
    def is_active(self):
        """
        Returns True if there is no returned_date value
        """
        return self.returned_date is None

