from django.urls import path
from . import views

urlpatterns = [
    path('edit/', views.edit_profile, name='profiles.edit_profile'),
    path('view/', views.view_profile, name='profiles.view_profile'),
]
