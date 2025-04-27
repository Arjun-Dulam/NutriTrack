from django.urls import path
from . import views

# URL patterns for the accounts app.
urlpatterns = [
    # Route for user signup page.
    path('signup/', views.signup, name='accounts.signup'),

    # Route for user login page.
    path('login/', views.login, name='accounts.login'),

    # Route for user logout functionality.
    path('logout/', views.logout, name='accounts.logout'),

    # Route for user password change page.
    path('changePassword/', views.changePassword, name='accounts.changePassword'),
]
