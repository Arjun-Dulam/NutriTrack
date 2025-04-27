from django.apps import AppConfig

# Configuration for the 'nutrition' app
class NutritionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # Default primary key field type
    name = "nutrition"  # App's label (important for Django settings and app structure)
