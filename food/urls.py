from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.food_list, name='food.list'),
    path('add_log/', views.add_food_log, name='add_food_log'),
    path('remove_log/<int:log_id>/', views.remove_food_log, name='remove_food_log'),  # New URL pattern
    path('add_water_log/', views.add_water_log, name='add_water_log'),
    path('remove_water_log/<int:log_id>/', views.remove_water_log, name='remove_water_log'),  # New URL pattern
    path('add_exercise_log/', views.add_exercise_log, name='add_exercise_log'),
    path('remove_exercise_log/<int:log_id>/', views.remove_exercise_log, name='remove_exercise_log')
]