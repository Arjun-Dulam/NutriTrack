from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# Handles user logout. Only accessible if the user is logged in.
@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')


# Handles user login.
def login(request):
    template_data = {}
    template_data['title'] = 'Login'

    if request.method == 'GET':
        # Display the login form.
        return render(request, 'accounts/login.html', {'template_data': template_data})

    elif request.method == 'POST':
        # Process login form submission.
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            # If authentication fails, reload login page with error.
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            # If successful, log the user in and redirect.
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.username}! You have successfully logged in.')
            return redirect('home.index')


# Handles user signup (account creation).
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Auto-login after signup.
            return redirect('profiles.edit_profile')  # Redirect to edit profile page.
    else:
        form = UserCreationForm()

    # Render signup form.
    template_data = {'form': form}
    return render(request, 'accounts/signup.html', {'template_data': template_data})


# Handles user password change.
def changePassword(request):
    template_data = {}
    template_data['title'] = 'Change Password'

    if request.method == 'GET':
        # Display the change password form.
        return render(request, 'accounts/changePassword.html', {'template_data': template_data})

    elif request.method == 'POST':
        # Process the password change request.
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            # If passwords do not match, show an error.
            template_data['error'] = 'The new passwords do not match.'
            return render(request, 'accounts/changePassword.html', {'template_data': template_data})

        try:
            # Attempt to update the user's password.
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            template_data['success'] = f'Password for "{username}" was successfully changed.'
            return render(request, 'home/index.html', {'template_data': template_data})
        except User.DoesNotExist:
            # If user not found, show an error.
            template_data['error'] = 'Username not found.'
            return render(request, 'accounts/changePassword.html', {'template_data': template_data})


# Duplicate logout view (redundant with the one above).
# Suggestion: Keep only one logout view to avoid confusion.
@login_required
def logout(request):
    auth_logout(request)
    return render(request, 'accounts/logoutConfirmation.html')
