from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    username = forms.CharField(required=True)

    dietary_restrictions = forms.MultipleChoiceField(
        choices=UserProfile.DIETARY_RESTRICTIONS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = ['height_cm', 'weight_kg', 'sex', 'activity_level', 'dietary_restrictions']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username

        if self.instance and self.instance.dietary_restrictions:
            self.initial['dietary_restrictions'] = self.instance.dietary_restrictions.split(',')

    def save(self, commit=True):
        profile = super().save(commit=False)
        # Save the user’s username outside of the profile model
        if self.cleaned_data.get('username'):
            self.instance.user.username = self.cleaned_data['username']
            self.instance.user.save()
        if commit:
            profile.save()
        return profile

    def clean_dietary_restrictions(self):
        data = self.cleaned_data.get('dietary_restrictions')
        return ','.join(data)