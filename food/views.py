from django.shortcuts import render
from django.conf import settings
import requests

# Create your views here.
def food_list(request):
    query = request.GET.get('query', '').strip()  # Get the query and strip whitespace
    if not query:  # If no query is provided
        return render(request, 'food/food_list.html', {'message': 'Search for your favorite foods!'})

    api_key = settings.SPOONACULAR_API_KEY
    url = f"https://api.spoonacular.com/food/menuItems/search"
    params = {
        'query': query,
        'number': 5,
        'apiKey': api_key,
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        error_message = response.json().get('message', 'An error occurred while fetching data.')
        return render(request, 'food/food_list.html', {'error': error_message, 'query': query})
    
    data = response.json()
    food_items = data.get('menuItems', [])

    # Handle missing images by assigning a placeholder
    for item in food_items:
        if not item.get('image'):  # If the image field is missing or empty
            item['image'] = 'https://via.placeholder.com/100'  # Placeholder image URL

    for item in food_items:
        print(item.get('image', 'No image available'))
    
    return render(request, 'food/food_list.html', {'food_items': food_items, 'query': query})