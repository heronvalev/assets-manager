from django import forms
from .models import Asset, Assignment

# Asset Create/Edit form
class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'name',
            'category',
            'brand',
            'model',
            'os',
            'serial_number',
            'purchase_date',
            'status',
            'location',
            'notes'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'os': forms.Select(attrs={'class': 'form-select'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

# Assignment Create form
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            'asset',
            'entra_user',
            'assigned_date',
            'location',
            'assignment_reason',
            'notes'
        ]
        widgets = {
            'assigned_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'assignment_reason': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'asset': forms.Select(attrs={'class': 'form-select'}),
            'entra_user': forms.Select(attrs={'class': 'form-select'}),
        }

# Assignment edit form page
class AssignmentEditForm(forms.ModelForm):
    class Meta:
        model = Assignment

        # Only some editable fields
        fields = ['returned_date', 'location', 'notes']

        widgets = {
            'returned_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }