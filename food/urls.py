from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.food_list, name='food.list'),
    path('add_log/', views.add_food_log, name='add_food_log'),
    path('remove_log/<int:log_id>/', views.remove_food_log, name='remove_food_log'),  # New URL pattern
]