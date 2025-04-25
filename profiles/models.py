from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)

    height_cm = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0)]
    )

    weight_kg = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0)]
    )

    DIETARY_RESTRICTIONS_CHOICES = [
        ('vegetarian', 'Vegetarian'),
        ('allergic_to_seafood', 'Allergic to Seafood'),
        ('peanuts', 'Allergic to Peanuts'),
        ('lactose_intolerant', 'Lactose Intolerant'),
    ]
    dietary_restrictions = models.TextField(
        blank=True,
        help_text="Comma‑separated dietary restrictions"
    )

    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary'),
        ('lightly_active', 'Lightly Active'),
        ('moderately_active', 'Moderately Active'),
        ('very_active', 'Very Active'),
        ('super_active', 'Super Active'),
    ]
    activity_level = models.CharField(
        max_length=50,
        choices=ACTIVITY_LEVEL_CHOICES,
        null=True, blank=True
    )

    def __str__(self):
        return self.user.username