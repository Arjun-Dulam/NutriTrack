from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class UserProfile(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    height_cm = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0)]
    )
    weight_kg = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0)]
    )
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)
    dietary_restrictions = models.TextField(blank=True)
    water_intake_liters = models.FloatField(default=0.0)
    calories_burned = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username