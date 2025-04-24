from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class FoodLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=200)
    spoonacular_id = models.IntegerField(null=True, blank=True) # Optional: Store Spoonacular ID if available
    calories = models.FloatField(null=True, blank=True)
    protein_g = models.FloatField(null=True, blank=True)
    carbs_g = models.FloatField(null=True, blank=True)
    fat_g = models.FloatField(null=True, blank=True)
    log_date = models.DateTimeField(default=timezone.now)
    # Optional: Add meal type (e.g., breakfast, lunch, dinner, snack)
    MEAL_CHOICES = [
        ('B', 'Breakfast'),
        ('L', 'Lunch'),
        ('D', 'Dinner'),
        ('S', 'Snack'),
    ]
    meal_type = models.CharField(max_length=1, choices=MEAL_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.food_name} on {self.log_date.strftime('%Y-%m-%d')}"
