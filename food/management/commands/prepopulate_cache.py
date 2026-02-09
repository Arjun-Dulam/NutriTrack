import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from food.models import FoodLog, NutritionCache


class Command(BaseCommand):
    help = 'Pre-populate NutritionCache from existing FoodLog entries with known spoonacular_ids'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cached without making API calls',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Find unique spoonacular_ids that aren't already cached
        logged_ids = (
            FoodLog.objects
            .filter(spoonacular_id__isnull=False)
            .values_list('spoonacular_id', flat=True)
            .distinct()
        )
        cached_ids = set(
            NutritionCache.objects
            .values_list('spoonacular_id', flat=True)
        )
        ids_to_cache = [sid for sid in logged_ids if sid not in cached_ids]

        self.stdout.write(f"Found {len(ids_to_cache)} uncached spoonacular_ids to populate.")

        if dry_run:
            for sid in ids_to_cache:
                food_name = FoodLog.objects.filter(spoonacular_id=sid).values_list('food_name', flat=True).first()
                self.stdout.write(f"  Would cache: {food_name} (ID: {sid})")
            return

        api_key = settings.SPOONACULAR_API_KEY
        cached_count = 0
        error_count = 0

        for sid in ids_to_cache:
            food_name = FoodLog.objects.filter(spoonacular_id=sid).values_list('food_name', flat=True).first() or ''
            try:
                url = f"https://api.spoonacular.com/recipes/{sid}/nutritionWidget.json?apiKey={api_key}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                NutritionCache.objects.create(
                    spoonacular_id=sid,
                    food_name=food_name,
                    calories=float(data.get('calories', '0').replace('kcal', '').strip() or 0),
                    protein_g=float(data.get('protein', '0').replace('g', '').strip() or 0),
                    carbs_g=float(data.get('carbs', '0').replace('g', '').strip() or 0),
                    fat_g=float(data.get('fat', '0').replace('g', '').strip() or 0),
                    raw_api_response=data,
                    access_count=1,
                )
                cached_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Cached: {food_name} (ID: {sid})"))
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"  Failed: {food_name} (ID: {sid}) - {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Cached: {cached_count}, Errors: {error_count}"
        ))
