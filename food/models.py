from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Model to store food logs
class FoodLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=200)
    spoonacular_id = models.IntegerField(null=True, blank=True)  # External API ID (optional)
    calories = models.FloatField(null=True, blank=True)
    protein_g = models.FloatField(null=True, blank=True)
    carbs_g = models.FloatField(null=True, blank=True)
    fat_g = models.FloatField(null=True, blank=True)
    log_date = models.DateTimeField(default=timezone.now)

    # Optional meal type field
    MEAL_CHOICES = [
        ('B', 'Breakfast'),
        ('L', 'Lunch'),
        ('D', 'Dinner'),
        ('S', 'Snack'),
    ]
    meal_type = models.CharField(max_length=1, choices=MEAL_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.food_name} on {self.log_date.strftime('%Y-%m-%d')}"

# Model to store water intake logs
class WaterLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    water_amount_ml = models.FloatField()  # Amount in milliliters
    log_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.water_amount_ml} ml on {self.log_date.strftime('%Y-%m-%d')}"

# Model to store exercise logs
class ExerciseLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise_name = models.CharField(max_length=200)
    calories_burned = models.FloatField()
    log_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.exercise_name} on {self.log_date.strftime('%Y-%m-%d')}"
