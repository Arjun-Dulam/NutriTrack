from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.food_list, name='food.list'),
    path('add_log/', views.add_food_log, name='add_food_log'),
]