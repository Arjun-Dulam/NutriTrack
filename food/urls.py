from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.food_list, name='food.list'),
    
]
