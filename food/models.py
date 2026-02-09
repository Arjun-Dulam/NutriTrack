from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

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


# Cache nutrition data by spoonacular_id to avoid redundant API calls
class NutritionCache(models.Model):
    spoonacular_id = models.IntegerField(unique=True, db_index=True)
    food_name = models.CharField(max_length=200)
    calories = models.FloatField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fat_g = models.FloatField()
    raw_api_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    access_count = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = "Nutrition cache entries"

    def __str__(self):
        return f"{self.food_name} (ID: {self.spoonacular_id}) - {self.access_count} hits"


# Track daily cache performance metrics
class CacheMetrics(models.Model):
    date = models.DateField(unique=True, default=date.today)
    cache_hits = models.IntegerField(default=0)
    cache_misses = models.IntegerField(default=0)
    api_calls_saved = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Cache metrics"
        ordering = ['-date']

    @property
    def total_requests(self):
        return self.cache_hits + self.cache_misses

    @property
    def hit_rate(self):
        total = self.total_requests
        if total == 0:
            return 0.0
        return round((self.cache_hits / total) * 100, 1)

    def __str__(self):
        return f"{self.date} - {self.hit_rate}% hit rate ({self.total_requests} requests)"
