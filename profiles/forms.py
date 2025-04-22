from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['height_cm', 'weight_kg', 'sex', 'dietary_restrictions', 'activity_level']
        widgets = {
            'dietary_restrictions': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'sex': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'activity_level': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        }