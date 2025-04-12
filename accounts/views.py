from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html',
                      {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            template_data['error'] =  \
                'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')


def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = UserCreationForm()
        return render(request, 'accounts/signup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html',
                {'template_data': template_data})

@login_required            
def changePassword(request):
    template_data = {}
    template_data['title'] = 'Change Password'
    if request.method == 'GET':
        return render(request, 'accounts/changePassword.html',
                      {'template_data': template_data})
    elif request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            template_data['error'] = 'The current password is incorrect.'
            return render(request, 'accounts/changePassword.html', {'template_data': template_data})

        if new_password != confirm_password:
            template_data['error'] = 'The new passwords do not match.'
            return render(request, 'accounts/changePassword.html', {'template_data': template_data})

        request.user.set_password(new_password)
        request.user.save()
        template_data['success'] = 'Your password has been successfully changed.'
        return render(request, 'accounts/changePassword.html', {'template_data': template_data})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')