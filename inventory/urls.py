from django.urls import path
from . import views

urlpatterns = [
    path('assets/', views.asset_list, name='asset_list'),
    path('assignments', views.assignment_list, name='assignment_list'),
    path('assets/<int:asset_id>/', views.asset_details, name='asset_details'),
    path('users/<int:user_id>/assignments/', views.user_assignments, name='user_assignments'),
    path('users/', views.user_list, name='user_list'),
    path('assets/add/', views.create_asset, name='create_asset'),
]
