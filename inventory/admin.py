from django.contrib import admin
from .models import Asset, Assignment

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'category', 'status', 'location')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('asset', 'assigned_upn', 'assigned_date', 'returned_date')
