from django.urls import path
from . import views

#path method takes in the:
# 1) the route to be accessed,
# 2) the view method from views.py,
# 3) name given to the path to uniquely distinguish in the django project
app_name = 'home'
urlpatterns = [
    path('', views.index, name= 'index'),
    path('about', views.about, name = 'about')
]