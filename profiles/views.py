from django.shortcuts import render, redirect
from .forms import UserProfileForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required

# View for editing the user's profile, probably require login for this
# @login_required  # (optional) Decorator to require login
def edit_profile(request):
    # Get or create a profile for the current user
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Populate the form with POST data
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profiles.view_profile')  # Redirect to view profile after saving
    else:
        # Populate the form with the existing profile data
        form = UserProfileForm(instance=profile, user=request.user)

    return render(request, 'profiles/edit_profile.html', {'form': form})

# View for displaying the user's profile
@login_required
def view_profile(request):
    # Get or create a profile for the current user
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    return render(request, 'profiles/view_profile.html', {'profile': profile})
