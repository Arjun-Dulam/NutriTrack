from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from profiles.models import UserProfile
import requests

@login_required
def food_list(request):
    query = request.GET.get('query', '').strip()  # Get the query and strip whitespace
    if not query:  # If no query is provided
        return render(request, 'food/list.html', {'message': 'Search for your favorite foods!'})

    # Get the user's dietary restrictions
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        restrictions_str = user_profile.dietary_restrictions or ""
    except UserProfile.DoesNotExist:
        restrictions_str = ""  # Default to no restrictions if profile doesn't exist

    # Parse dietary restrictions into a list
    restrictions_list = [r.strip() for r in restrictions_str.split(',') if r.strip()]

    # Map restrictions to Spoonacular API parameters
    diet_param = None
    intolerances_param = []

    if 'vegetarian' in restrictions_list:
        diet_param = 'vegetarian'
        restrictions_list.remove('vegetarian')

    # Map remaining restrictions to Spoonacular intolerances
    intolerance_mapping = {
        'allergic_to_seafood': ['Seafood', 'Shellfish'],
        'peanuts': ['Peanut'],
        'lactose_intolerant': ['Dairy'],
    }
    for restriction in restrictions_list:
        if restriction in intolerance_mapping:
            intolerances_param.extend(intolerance_mapping[restriction])

    # Prepare API request
    api_key = settings.SPOONACULAR_API_KEY
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        'query': query,
        'number': 50,
        'apiKey': api_key,
        'addRecipeInformation': True,  # Include detailed recipe info
    }

    if diet_param:
        params['diet'] = diet_param
    if intolerances_param:
        params['intolerances'] = ','.join(intolerances_param)

    # Make the API request
    response = requests.get(url, params=params)
    if response.status_code != 200:
        error_message = response.json().get('message', 'An error occurred while fetching data.')
        return render(request, 'food/list.html', {'error': error_message, 'query': query})

    # Parse the API response
    data = response.json()
    food_items = data.get('results', [])

    # Render the results in the template
    return render(request, 'food/list.html', {'food_items': food_items, 'query': query})