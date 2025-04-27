from django.shortcuts import render, redirect
from groq import Groq
from django.conf import settings
from django.contrib.auth.decorators import login_required
from profiles.models import UserProfile
from django.utils.timezone import now
from food.models import FoodLog, ExerciseLog, WaterLog

# Initialize Groq API client using API key from Django settings
client = Groq(api_key=settings.GROQ_API_KEY)

# --------- Helper Functions ---------

def calculate_total_calories_eaten(user):
    """
    Calculate the total calories eaten by the user today.
    """
    today = now().date()
    food_logs = FoodLog.objects.filter(user=user, log_date__date=today)
    total_calories = sum(log.calories for log in food_logs)
    return total_calories

def calculate_total_exercise_calories(user):
    """
    Calculate the total calories burned during exercise today.
    """
    today = now().date()
    exercise_logs = ExerciseLog.objects.filter(user=user, log_date__date=today)
    total_calories = sum(log.calories_burned for log in exercise_logs)
    return total_calories

def calculate_maintenance_calories(weight_kg, height_cm, sex, activity_level, age=25):
    """
    Estimate daily maintenance calories (TDEE) using the Mifflin-St Jeor formula.
    Assumes default age 25 if not provided.
    """
    if sex.lower() == 'm':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    elif sex.lower() == 'f':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        raise ValueError("Sex must be 'male' or 'female'")

    activity_multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'super_active': 1.9
    }

    if activity_level.lower() not in activity_multipliers:
        raise ValueError("Invalid activity level.")

    return round(bmr * activity_multipliers[activity_level.lower()], 2)

def calculate_water_intake(weight_kg):
    """
    Estimate daily recommended water intake based on body weight.
    """
    water_ml = weight_kg * 35  # 35 ml per kg
    return round(water_ml / 1000, 2)  # Convert ml to liters

def llm_call(user_input):
    """
    Sends the user input to the Groq LLM and returns the model's response.
    """
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": user_input}],
        model="llama-3.3-70b-versatile",
        stream=False,
    )
    return response.choices[0].message.content

# --------- Views ---------

@login_required
def index(request):
    """
    Main dashboard view: displays user stats, water intake, calorie graphs, and LLM assistant.
    """

    # Fetch user profile details
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        restrictions_str = user_profile.dietary_restrictions or ""
    except UserProfile.DoesNotExist:
        user_profile = None
        restrictions_str = ""

    sex = user_profile.sex if user_profile else None
    height_cm = user_profile.height_cm if user_profile else None
    weight_kg = user_profile.weight_kg if user_profile else None
    activity_level = user_profile.activity_level if user_profile else None
    restrictions_list = [r.strip() for r in restrictions_str.split(',') if r.strip()]

    calories_needed = water_intake = None
    if user_profile:
        calories_needed = calculate_maintenance_calories(weight_kg, height_cm, sex, activity_level)
        water_intake = calculate_water_intake(weight_kg)

    total_calories_eaten = calculate_total_calories_eaten(request.user)
    total_exercise_calories = calculate_total_exercise_calories(request.user)

    today = now().date()
    water_logs = WaterLog.objects.filter(user=request.user, log_date__date=today)
    water_intake_logged = sum(log.water_amount_ml for log in water_logs) / 1000  # Convert ml to liters

    llm_response = None
    user_question = None

    # Handle user's nutrition-related question to LLM
    if request.method == 'POST':
        user_question = request.POST.get('question')
        if user_question:
            llm_response = llm_call(user_question)

    return render(request, 'home/index.html', {
        'joke': llm_response,
        'sex': sex,
        'height_cm': height_cm,
        'weight_kg': weight_kg,
        'activity_level': activity_level,
        'calories': calories_needed,
        'user_question': user_question,
        'water_intake': water_intake,
        'water_intake_logged': water_intake_logged,
        'total_calories_eaten': total_calories_eaten,
        'exercise_calories': total_exercise_calories,
        'maintenance_calories': calories_needed,
    })

def about(request):
    """
    View to render the About page.
    """
    return render(request, 'home/about.html')

def contact(request):
    """
    View to render the Contact page.
    """
    return render(request, 'home/contact.html')

def services(request):
    """
    View to render the Services page.
    """
    return render(request, 'home/services.html')
