from django.shortcuts import render, redirect
from .forms import UserProfileForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profiles.view_profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    return render(request, 'profiles/edit_profile.html', {'form': form})

@login_required
def view_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    return render(request, 'profiles/view_profile.html', {'profile': profile})