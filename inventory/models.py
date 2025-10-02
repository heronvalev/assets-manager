from django.db import models
from django.utils import timezone

# Operating System (OS) options 
class OSOption(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
# Entra Users table to sync with Microsoft Graph API
class EntraUser(models.Model):
    entra_user_id = models.CharField(max_length=36, unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    upn = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    department = models.CharField(max_length=50, blank=True)
    deleted_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.display_name} ({self.upn})"
    
# Assets table for all assets/devices    
class Asset(models.Model):

    STATUS_OPERATIONAL = "Operational"
    STATUS_MAINTENANCE = "Maintenance"
    STATUS_DECOMMISSIONED = "Decommissioned"
    STATUS_LOST = "Lost/Damaged"
    STATUS_PENDING = "Pending Setup"
    STATUS_RESERVED = "Reserved"

    STATUS_CHOICES = [
        (STATUS_OPERATIONAL, "Operational"),
        (STATUS_MAINTENANCE, "Maintenance"),
        (STATUS_DECOMMISSIONED, "Decommissioned"),
        (STATUS_LOST, "Lost/Damaged"),
        (STATUS_PENDING, "Pending Setup"),
        (STATUS_RESERVED, "Reserved"),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)
    os = models.ForeignKey(OSOption, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="OS")
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPERATIONAL)
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
 
    def get_current_user(self):
        """
        Returns the EntraUser object currently assigned, or None.
        """
        active_assignment = self.assignments.filter(returned_date__isnull=True).first()
        if active_assignment:
            return active_assignment.entra_user
        return None
        
# Assignments table to track current and historical asset assignment    
class Assignment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="assignments")
    entra_user = models.ForeignKey(EntraUser, null=True, blank=True, on_delete=models.SET_NULL, related_name="user_assignments")
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
    
    def save(self, *args, **kwargs):
        """
        Override of the Assignment model's save method.

        Behavior:
        - Calls the default save() to persist changes to the Assignment.
        - If a returned_date is being set on an assignment that was previously active,
          the related Asset's status is automatically updated to 'Maintenance' and saved.
        - Once an assignment is closed (returned_date filled), the asset enters
            'Maintenance' status until IT prepares it for reuse.
        Args:
            *args: Positional arguments passed to the base save() method.
            **kwargs: Keyword arguments passed to the base save() method.  
        """
        if self.pk:  # Check if this assignment already exists in the DB

            old_assignment = Assignment.objects.get(pk=self.pk)
            was_active = not old_assignment.returned_date
        else:

            was_active = False  # New objects can’t trigger the status change

        super().save(*args, **kwargs)

        if self.returned_date and was_active:

            self.asset.status = Asset.STATUS_MAINTENANCE
            self.asset.save()
