from django.urls import path
from . import views

# Define URL patterns for the profiles app
urlpatterns = [
    path('edit/', views.edit_profile, name='profiles.edit_profile'),  # URL for editing profile
    path('view/', views.view_profile, name='profiles.view_profile'),  # URL for viewing profile
]
