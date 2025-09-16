from django.urls import path
from . import views

urlpatterns = [
    path('assets/', views.asset_list, name='asset_list'),
    path('assignments', views.assignment_list, name='assignment_list'),
]
