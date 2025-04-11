from django.shortcuts import render, redirect

# Create your views here.

def index(request):
    return (request,' home/index.html')

def about(request):
    return (request,' home/about.html')