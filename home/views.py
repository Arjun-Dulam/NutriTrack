from django.shortcuts import render, redirect
from groq import Groq
from django.conf import settings
from django.contrib.auth.decorators import login_required
from profiles.models import UserProfile

client = Groq(
    api_key=settings.GROQ_API_KEY,
)


# Create your views here.

@login_required
def index(request):
    # Fetch user profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        restrictions_str = user_profile.dietary_restrictions or ""
    except UserProfile.DoesNotExist:
        user_profile = None
        restrictions_str = ""

    # Prepare profile data
    sex = user_profile.sex if user_profile else None
    height_cm = user_profile.height_cm if user_profile else None
    weight_kg = user_profile.weight_kg if user_profile else None
    activity_level = user_profile.activity_level if user_profile else None
    restrictions_list = [r.strip() for r in restrictions_str.split(',') if r.strip()]

    # Calculate calories (only if profile exists)
    calories_needed = None
    if user_profile:
        calories_needed = calculate_maintenance_calories(weight_kg, height_cm, sex, activity_level)
        water_intake = calculate_water_intake(weight_kg)

    llm_response = None
    user_question = None

    # Handle form POST
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
    })


def about(request):
    return render(request, 'home/about.html')

def contact(request):
    return render(request, 'home/contact.html')

def services(request):
    return render(request, 'home/services.html')



def llm_call(user_input):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": user_input}],
        model="llama-3.3-70b-versatile",
        stream=False,
    )
    return response.choices[0].message.content


def calculate_maintenance_calories(weight_kg, height_cm, sex, activity_level, age =25):
    """
    Calculate daily maintenance calories (TDEE).

    Args:
        weight_kg (float): Weight in kilograms
        height_cm (float): Height in centimeters
        age (int): Age in years
        sex (str): 'male' or 'female'
        activity_level (str): 'sedentary', 'light', 'moderate', 'active', 'super'

    Returns:
        float: TDEE (Total Daily Energy Expenditure)
    """
    # BMR Calculation (Mifflin-St Jeor Equation)
    if sex.lower() == 'm':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    elif sex.lower() == 'f':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        raise ValueError("Sex must be 'male' or 'female'")

    # Activity Multipliers
    activity_multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'super_active': 1.9
    }


    if activity_level.lower() not in activity_multipliers:
        raise ValueError("Invalid activity level. Choose from: 'sedentary', 'light', 'moderate', 'active', 'super'.")

    # Calculate TDEE
    tdee = bmr * activity_multipliers[activity_level]

    return round(tdee, 2)

def calculate_water_intake(weight_kg):
    """
    Calculate recommended daily water intake based on weight.

    Args:
        weight_kg (float): Weight in kilograms

    Returns:
        float: Water intake in liters
    """
    # 35 ml of water per kg of body weight
    water_ml = weight_kg * 35
    water_liters = water_ml / 1000  # Convert to liters
    return round(water_liters, 2)

