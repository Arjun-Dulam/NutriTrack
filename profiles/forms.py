from django import forms
from .models import UserProfile

DIETARY_RESTRICTIONS_CHOICES = [
    ('vegetarian', 'Vegetarian'),
    ('allergic_to_seafood', 'Allergic to Seafood'),
    ('peanuts', 'Allergic to Peanuts'),
    ('lactose_intolerant', 'Lactose Intolerant'),
]

class UserProfileForm(forms.ModelForm):
    dietary_restrictions = forms.MultipleChoiceField(
        choices=DIETARY_RESTRICTIONS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    class Meta:
        model = UserProfile
        fields = ['height_cm', 'weight_kg', 'sex', 'activity_level', 'dietary_restrictions']
        widgets = {
            'sex': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'activity_level': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing, split the stored string into a list for the multiple select field.
        if self.instance and self.instance.dietary_restrictions:
            self.initial['dietary_restrictions'] = self.instance.dietary_restrictions.split(',')

    def clean_dietary_restrictions(self):
        data = self.cleaned_data.get('dietary_restrictions')
        # Join the list using commas (or any delimiter of your choice)
        return ','.join(data)