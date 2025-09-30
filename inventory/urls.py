from django.urls import path
from . import views

urlpatterns = [
    path('assets/', views.asset_list, name='asset_list'),
    path('assignments', views.assignment_list, name='assignment_list'),
    path('assets/<int:asset_id>/', views.asset_details, name='asset_details'),
    path('users/<int:user_id>/assignments/', views.user_assignments, name='user_assignments'),
    path('users/', views.user_list, name='user_list'),
    path('assets/add/', views.create_asset, name='create_asset'),
    path('assets/<int:asset_id>/edit/', views.edit_asset, name='edit_asset'),
    path('assignments/add/', views.create_assignment, name='create_assignment'),
    path('assignments/<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('login/', views.ms_login, name='ms_login'),
    path('callback/', views.ms_callback, name='ms_callback'),
    path('logout/', views.ms_logout, name='ms_logout'),
    path('', views.home, name='home'),
    path('assets/<int:asset_id>/delete/', views.asset_delete, name='asset_confirm_delete'),
]
