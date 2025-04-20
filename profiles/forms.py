from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['height_cm', 'weight_kg', 'sex', 'dietary_restrictions', 'water_intake_liters', 'calories_burned']
        widgets = {
            'dietary_restrictions': forms.Textarea(attrs={'rows': 2}),
        }