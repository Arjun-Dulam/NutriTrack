from django.shortcuts import render, redirect # Added redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from profiles.models import UserProfile
import requests
from .models import FoodLog, WaterLog, ExerciseLog
from django.utils import timezone # Import timezone
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


@login_required
def food_list(request):
    query = request.GET.get('query', '').strip()  # Get the query and strip whitespace
    page = int(request.GET.get('page', 1))  # Get the current page, default to 1
    logged_foods = FoodLog.objects.filter(user=request.user).order_by('-log_date')  # Fetch logged foods
    water_logs = WaterLog.objects.filter(user=request.user).order_by('-log_date')  # Fetch water logs

    if not query:  # If no query is provided
        return render(request, 'food/list.html', {
            'message': 'Search for your favorite foods!',
            'logged_foods': logged_foods,
            'water_logs': water_logs  # Include water logs
        })

    # Prepare API request
    api_key = settings.SPOONACULAR_API_KEY
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        'query': query,
        'number': 5,  # Limit the number of results to 5
        'offset': (page - 1) * 5,  # Offset based on the current page
        'apiKey': api_key,
        'addRecipeInformation': True,  # Include detailed recipe info
    }

    # Make the API request
    response = requests.get(url, params=params)
    if response.status_code != 200:
        error_message = response.json().get('message', 'An error occurred while fetching data.')
        return render(request, 'food/list.html', {
            'error': error_message,
            'query': query,
            'logged_foods': logged_foods
        })

    # Parse the API response
    data = response.json()
    food_items = data.get('results', [])
    

    # Handle AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check if the request is AJAX
        return JsonResponse({'food_items': food_items})

    # Render the results in the template
    return render(request, 'food/list.html', {
        'food_items': food_items,
        'query': query,
        'logged_foods': logged_foods,
        'water_logs': water_logs,  # Pass water logs to the template
        'page': page,
    })

@login_required
def add_food_log(request):
    if request.method == 'POST':
        food_name = request.POST.get('food_name')
        # Ensure the ID from the form is treated as an integer if it exists
        spoonacular_id_str = request.POST.get('spoonacular_id')
        spoonacular_id = int(spoonacular_id_str) if spoonacular_id_str and spoonacular_id_str.isdigit() else None

        # --- Fetch detailed nutrition info from Spoonacular using Recipe ID ---
        calories = None
        protein_g = None
        carbs_g = None
        fat_g = None

        # Use the recipe ID (spoonacular_id) to get nutrition info
        if spoonacular_id:
            try:
                api_key = settings.SPOONACULAR_API_KEY
                # Use the recipe nutrition endpoint
                url = f"https://api.spoonacular.com/recipes/{spoonacular_id}/nutritionWidget.json?apiKey={api_key}"
                response = requests.get(url)
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                data = response.json()

                # Extract nutrition info - Adjust keys based on actual API response
                calories = data.get('calories') # Often a string like "350 kcal"
                protein_g = data.get('protein') # Often a string like "20g"
                carbs_g = data.get('carbs')   # Often a string like "40g"
                fat_g = data.get('fat')     # Often a string like "15g"

                # Basic parsing (remove 'kcal' or 'g', convert to float)
                # More robust parsing might be needed depending on API variations
                try:
                    calories = float(calories.replace('kcal', '').strip()) if calories else None
                    protein_g = float(protein_g.replace('g', '').strip()) if protein_g else None
                    carbs_g = float(carbs_g.replace('g', '').strip()) if carbs_g else None
                    fat_g = float(fat_g.replace('g', '').strip()) if fat_g else None
                except (ValueError, AttributeError):
                     # Handle cases where parsing fails or data is not as expected
                     print(f"Could not parse nutrition data: Cals={calories}, Prot={protein_g}, Carb={carbs_g}, Fat={fat_g}")
                     calories, protein_g, carbs_g, fat_g = None, None, None, None # Reset on failure

            except requests.exceptions.RequestException as e:
                print(f"Error fetching nutrition data from Spoonacular: {e}")
                # Optionally add a Django message: messages.error(request, "Could not fetch nutrition details.")
            except Exception as e:
                print(f"Error processing nutrition data: {e}")
                # Optionally add a Django message

        # --- Create and save the FoodLog entry ---
        if food_name: # Ensure we have at least a name
            FoodLog.objects.create(
                user=request.user,
                food_name=food_name,
                spoonacular_id=spoonacular_id,
                calories=calories,
                protein_g=protein_g,
                carbs_g=carbs_g,
                fat_g=fat_g,
                log_date=timezone.now() # Use timezone.now()
                # meal_type could be added later via a dropdown in the form
            )
            # Redirect after POST to prevent duplicate submissions
            # Redirect to a page showing the log, or back to search for now
            # messages.success(request, f"'{food_name}' added to your log.") # Example message
            return redirect('food.list') # Redirect back to the search results/list page

    # If not POST or if required data is missing, redirect
    # Or render an error message
    # messages.error(request, "Invalid request to add food log.") # Example message
    return redirect('food.list') # Redirect back

@login_required
def remove_food_log(request, log_id):
    food_log = get_object_or_404(FoodLog, id=log_id, user=request.user)
    food_log.delete()
    return redirect('food.list')  # Redirect back to the food list page

@login_required
def add_water_log(request):
    if request.method == 'POST':
        water_amount = request.POST.get('water_amount')
        if water_amount:
            WaterLog.objects.create(
                user=request.user,
                water_amount_ml=float(water_amount),
                log_date=timezone.now()
            )
    return redirect('food.list')  # Redirect back to the same page

@login_required
def remove_water_log(request, log_id):
    water_log = get_object_or_404(WaterLog, id=log_id, user=request.user)
    water_log.delete()
    return redirect('food.list')  # Redirect back to the food list page

@login_required
def add_exercise_log(request):
    if request.method == 'POST':
        exercise_name = request.POST.get('exercise_name')
        calories_burned = request.POST.get('calories_burned')
        duration_minutes = request.POST.get('duration_minutes')

        if exercise_name and calories_burned and duration_minutes:
            ExerciseLog.objects.create(
                user=request.user,
                exercise_name=exercise_name,
                calories_burned=float(calories_burned),
                duration_minutes=float(duration_minutes),
                log_date=timezone.now()
            )
    return redirect('food.list')  # Redirect back to the same page


@login_required
def remove_exercise_log(request, log_id):
    exercise_log = get_object_or_404(ExerciseLog, id=log_id, user=request.user)
    exercise_log.delete()
    return redirect('food.list')  # Redirect back to the food list page