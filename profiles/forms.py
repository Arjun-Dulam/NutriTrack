from django import forms
from .models import UserProfile

# Define a ModelForm for the UserProfile model
class UserProfileForm(forms.ModelForm):
    # Extra field for username (not directly in UserProfile model)
    username = forms.CharField(required=True)

    # Multiple choice field for dietary restrictions with checkbox widget
    dietary_restrictions = forms.MultipleChoiceField(
        choices=UserProfile.DIETARY_RESTRICTIONS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = ['height_cm', 'weight_kg', 'sex', 'activity_level', 'dietary_restrictions']

    def __init__(self, *args, **kwargs):
        # Pop user from kwargs if passed
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Initialize username field with the user's username
            self.fields['username'].initial = user.username

        # Initialize dietary restrictions field as list if data exists
        if self.instance and self.instance.dietary_restrictions:
            self.initial['dietary_restrictions'] = self.instance.dietary_restrictions.split(',')

    def save(self, commit=True):
        # Save the profile data and update the associated User's username
        profile = super().save(commit=False)
        if self.cleaned_data.get('username'):
            self.instance.user.username = self.cleaned_data['username']
            self.instance.user.save()
        if commit:
            profile.save()
        return profile

    def clean_dietary_restrictions(self):
        # Convert the list of dietary restrictions into a comma-separated string
        data = self.cleaned_data.get('dietary_restrictions')
        return ','.join(data)
