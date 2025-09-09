from django.db import models

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
        return self.assignments.filter(returned_date__isnull=True).exists()
    
class Assignment(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="assignments")
    entra_user_id = models.CharField(max_length=36)
    assigned_upn = models.EmailField(blank=True, null=True)
    assigned_date = models.DateField(auto_now_add=True)
    returned_date = models.DateField(blank=True, null=True)
    assignment_reason = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.asset.name} -> {self.assigned_upn or 'Unassigned'}"
    
    def is_active(self):
        return self.returned_date is None
