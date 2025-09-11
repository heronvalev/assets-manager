from django.contrib import admin
from .models import EntraUser, Asset, Assignment

@admin.register(EntraUser)
class EntraUserAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'upn', 'department', 'is_active')
    search_fields = ('display_name', 'upn')
    list_filter = ('is_active', 'department')

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'category', 'status', 'location')
    search_fields = ('name', 'serial_number', 'brand', 'model')
    list_filter = ('status', 'category', 'brand')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('asset', 'entra_user', 'assigned_date', 'returned_date')
    search_fields = ('asset__name', 'entra_user__display_name', 'entra_user__upn', 'location')
    list_filter = ('returned_date', 'location', 'assignment_reason')
