from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from profiles.models import UserProfile
from .models import FoodLog, WaterLog, ExerciseLog, NutritionCache, CacheMetrics
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum, F
from django.utils.timezone import now as tz_now
from datetime import date
from groq import Groq
import requests

# Set up the Groq API client
client = Groq(api_key=settings.GROQ_API_KEY)

# View for searching foods and listing logs
@login_required
def food_list(request):
    query = request.GET.get('query', '').strip()
    page = int(request.GET.get('page', 1))
    diet = request.GET.get('diet', '').strip()
    intolerances = request.GET.get('intolerances', '').strip()

    # Fetch logged data
    logged_foods = FoodLog.objects.filter(user=request.user).order_by('-log_date')
    water_logs = WaterLog.objects.filter(user=request.user).order_by('-log_date')
    exercise_logs = ExerciseLog.objects.filter(user=request.user).order_by('-log_date')

    # Stringify data for LLM
    food_string = ', '.join(logged_foods.values_list('food_name', flat=True))
    exercise_string = ', '.join(exercise_logs.values_list('exercise_name', flat=True))
    water_amounts = water_logs.values_list('water_amount_ml', flat=True)
    water_string = ', '.join([f"{amount} ml" for amount in water_amounts])
    total_water = WaterLog.objects.filter(user=request.user).aggregate(total=Sum('water_amount_ml'))['total'] or 0

    llm_response = None
    if request.method == 'POST' and 'llm_question' in request.POST:
        user_question = request.POST.get('llm_question')
        system_prompt = create_system_prompt(food_string, exercise_string, total_water)
        llm_response = llm_call(user_question, system_prompt)

    if not query:
        return render(request, 'food/list.html', {
            'message': 'Search for your favorite foods!',
            'logged_foods': logged_foods,
            'water_logs': water_logs,
            'exercise_logs': exercise_logs,
            'llm_response': llm_response,
        })

    # Prepare external API request to Spoonacular
    api_key = settings.SPOONACULAR_API_KEY
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = {
        'query': query,
        'number': 10,
        'offset': (page - 1) * 5,
        'apiKey': api_key,
        'addRecipeInformation': True,
    }
    if diet:
        params['diet'] = diet
    if intolerances:
        params['intolerances'] = intolerances

    response = requests.get(url, params=params)
    if response.status_code != 200:
        error_message = response.json().get('message', 'An error occurred.')
        return render(request, 'food/list.html', {
            'error': error_message,
            'query': query,
            'logged_foods': logged_foods
        })

    data = response.json()
    food_items = data.get('results', [])

    # Return AJAX responses for "Load More"
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'food_items': food_items})

    return render(request, 'food/list.html', {
        'food_items': food_items,
        'query': query,
        'logged_foods': logged_foods,
        'water_logs': water_logs,
        'page': page,
        'llm_response': llm_response,
        'exercise_logs': exercise_logs,
    })

# Add a food log entry (with database-backed nutrition cache)
@login_required
def add_food_log(request):
    if request.method == 'POST':
        food_name = request.POST.get('food_name')
        spoonacular_id_str = request.POST.get('spoonacular_id')
        spoonacular_id = int(spoonacular_id_str) if spoonacular_id_str and spoonacular_id_str.isdigit() else None

        calories = protein_g = carbs_g = fat_g = None

        # Fetch detailed nutrition info with cache-aside pattern
        if spoonacular_id:
            cache_entry = NutritionCache.objects.filter(spoonacular_id=spoonacular_id).first()

            if cache_entry:
                # CACHE HIT - use cached data
                calories = cache_entry.calories
                protein_g = cache_entry.protein_g
                carbs_g = cache_entry.carbs_g
                fat_g = cache_entry.fat_g

                # Update access metadata
                NutritionCache.objects.filter(pk=cache_entry.pk).update(
                    access_count=F('access_count') + 1,
                    last_accessed=tz_now(),
                )
                _record_cache_hit()
            else:
                # CACHE MISS - fetch from Spoonacular API
                try:
                    api_key = settings.SPOONACULAR_API_KEY
                    url = f"https://api.spoonacular.com/recipes/{spoonacular_id}/nutritionWidget.json?apiKey={api_key}"
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()

                    # Parse nutrition info
                    calories = float(data.get('calories', '0').replace('kcal', '').strip() or 0)
                    protein_g = float(data.get('protein', '0').replace('g', '').strip() or 0)
                    carbs_g = float(data.get('carbs', '0').replace('g', '').strip() or 0)
                    fat_g = float(data.get('fat', '0').replace('g', '').strip() or 0)

                    # Store in cache for future lookups
                    NutritionCache.objects.create(
                        spoonacular_id=spoonacular_id,
                        food_name=food_name or '',
                        calories=calories,
                        protein_g=protein_g,
                        carbs_g=carbs_g,
                        fat_g=fat_g,
                        raw_api_response=data,
                        access_count=1,
                    )
                except Exception as e:
                    print(f"Error fetching or parsing nutrition data: {e}")

                _record_cache_miss()

        if food_name:
            FoodLog.objects.create(
                user=request.user,
                food_name=food_name,
                spoonacular_id=spoonacular_id,
                calories=calories,
                protein_g=protein_g,
                carbs_g=carbs_g,
                fat_g=fat_g,
                log_date=timezone.now()
            )
    return redirect('food.list')

# Remove a food log entry
@login_required
def remove_food_log(request, log_id):
    food_log = get_object_or_404(FoodLog, id=log_id, user=request.user)
    food_log.delete()
    return redirect('food.list')

# Add a water intake log
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
    return redirect('food.list')

# Remove a water intake log
@login_required
def remove_water_log(request, log_id):
    water_log = get_object_or_404(WaterLog, id=log_id, user=request.user)
    water_log.delete()
    return redirect('food.list')

# Add an exercise log
@login_required
def add_exercise_log(request):
    if request.method == 'POST':
        exercise_name = request.POST.get('exercise_name')
        calories_burned = request.POST.get('calories_burned')
        if exercise_name and calories_burned:
            ExerciseLog.objects.create(
                user=request.user,
                exercise_name=exercise_name,
                calories_burned=float(calories_burned),
                log_date=timezone.now()
            )
    return redirect('food.list')

# Remove an exercise log
@login_required
def remove_exercise_log(request, log_id):
    exercise_log = get_object_or_404(ExerciseLog, id=log_id, user=request.user)
    exercise_log.delete()
    return redirect('food.list')

# Helper function to create a system prompt for LLM
def create_system_prompt(food_string, exercise_string, water_string):
    return f"""
    You are a helpful and friendly nutrition assistant. Always provide concise, factual answers.
    User's logged foods: {food_string}
    User's logged exercises: {exercise_string}
    User's logged water intake: {water_string}.
    Responses should be in text paragraph format.
    """

# Helper function to call the LLM
def llm_call(user_input, system_prompt):
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        model="llama-3.3-70b-versatile",
        stream=False,
    )
    return response.choices[0].message.content


# Cache metrics helpers
def _record_cache_hit():
    metrics, _ = CacheMetrics.objects.get_or_create(date=date.today())
    CacheMetrics.objects.filter(pk=metrics.pk).update(
        cache_hits=F('cache_hits') + 1,
        api_calls_saved=F('api_calls_saved') + 1,
    )


def _record_cache_miss():
    metrics, _ = CacheMetrics.objects.get_or_create(date=date.today())
    CacheMetrics.objects.filter(pk=metrics.pk).update(
        cache_misses=F('cache_misses') + 1,
    )
