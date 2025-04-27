from django.urls import path
from . import views

# Define the URL patterns for the 'home' app
# Each path:
# 1) specifies a route,
# 2) maps it to a view method from views.py,
# 3) assigns a unique name for reverse URL lookup in templates or code

urlpatterns = [
    path('', views.index, name='home.index'),         # Root URL -> index view
    path('about', views.about, name='home.about'),     # /about -> about view
    path('contact', views.contact, name='home.contact'), # /contact -> contact view
    path('services', views.services, name='home.services'), # /services -> services view
]
