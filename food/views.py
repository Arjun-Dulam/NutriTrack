from django.shortcuts import render
from django.conf import settings
import requests

# Create your views here.
def food_list(request):
    api_key = settings.SPOONACULAR_API_KEY
    url = f"https://api.spoonacular.com/food/menuItems/search"
    params = {
        'query': 'pizza',  # Example query, you can make this dynamic
        'number': 10,      # Number of results to fetch
        'apiKey': api_key,
    }
    response = requests.get(url, params=params)
    data = response.json()

    # Pass the data to the template
    return render(request, 'food/food_list.html', {'food_items': data.get('menuItems', [])})