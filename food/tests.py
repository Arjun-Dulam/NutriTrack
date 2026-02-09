from datetime import date
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from .models import NutritionCache, CacheMetrics, FoodLog


class NutritionCacheModelTest(TestCase):
    def test_create_cache_entry(self):
        entry = NutritionCache.objects.create(
            spoonacular_id=12345,
            food_name="Grilled Chicken",
            calories=300.0,
            protein_g=35.0,
            carbs_g=0.0,
            fat_g=7.0,
        )
        self.assertEqual(entry.spoonacular_id, 12345)
        self.assertEqual(entry.access_count, 1)
        self.assertIsNotNone(entry.created_at)
        self.assertIsNotNone(entry.last_accessed)

    def test_unique_spoonacular_id(self):
        NutritionCache.objects.create(
            spoonacular_id=99999,
            food_name="Rice",
            calories=200.0, protein_g=4.0, carbs_g=45.0, fat_g=0.5,
        )
        with self.assertRaises(Exception):
            NutritionCache.objects.create(
                spoonacular_id=99999,
                food_name="Rice Duplicate",
                calories=200.0, protein_g=4.0, carbs_g=45.0, fat_g=0.5,
            )

    def test_str(self):
        entry = NutritionCache.objects.create(
            spoonacular_id=111,
            food_name="Salmon",
            calories=250.0, protein_g=30.0, carbs_g=0.0, fat_g=12.0,
            access_count=5,
        )
        self.assertIn("Salmon", str(entry))
        self.assertIn("5 hits", str(entry))


class CacheMetricsModelTest(TestCase):
    def test_hit_rate_calculation(self):
        metrics = CacheMetrics.objects.create(
            date=date.today(),
            cache_hits=75,
            cache_misses=25,
        )
        self.assertEqual(metrics.hit_rate, 75.0)
        self.assertEqual(metrics.total_requests, 100)

    def test_hit_rate_zero_requests(self):
        metrics = CacheMetrics.objects.create(
            date=date(2025, 1, 1),
            cache_hits=0,
            cache_misses=0,
        )
        self.assertEqual(metrics.hit_rate, 0.0)

    def test_str(self):
        metrics = CacheMetrics.objects.create(
            date=date(2025, 6, 15),
            cache_hits=3,
            cache_misses=1,
        )
        self.assertIn("75.0%", str(metrics))
        self.assertIn("4 requests", str(metrics))


class CacheAsidePatternTest(TestCase):
    """Test the cache-aside logic in add_food_log view."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")
        self.client.login(username="testuser", password="pass123")

    @patch("food.views.requests.get")
    def test_cache_miss_calls_api_and_stores(self, mock_get):
        """First time logging a food should call Spoonacular API and cache the result."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "calories": "350kcal",
            "protein": "30g",
            "carbs": "10g",
            "fat": "15g",
        }
        mock_get.return_value = mock_response

        self.client.post("/food/add_log/", {
            "food_name": "Grilled Chicken",
            "spoonacular_id": "716429",
        })

        # API should have been called
        mock_get.assert_called_once()

        # Cache entry should exist
        cache = NutritionCache.objects.get(spoonacular_id=716429)
        self.assertEqual(cache.food_name, "Grilled Chicken")
        self.assertEqual(cache.calories, 350.0)
        self.assertEqual(cache.protein_g, 30.0)
        self.assertEqual(cache.carbs_g, 10.0)
        self.assertEqual(cache.fat_g, 15.0)
        self.assertEqual(cache.access_count, 1)

        # Food log should exist
        log = FoodLog.objects.get(user=self.user, spoonacular_id=716429)
        self.assertEqual(log.calories, 350.0)

        # Metrics: 1 miss
        metrics = CacheMetrics.objects.get(date=date.today())
        self.assertEqual(metrics.cache_misses, 1)
        self.assertEqual(metrics.cache_hits, 0)

    @patch("food.views.requests.get")
    def test_cache_hit_skips_api(self, mock_get):
        """Second time logging the same food should use cache, not API."""
        # Pre-populate cache
        NutritionCache.objects.create(
            spoonacular_id=716429,
            food_name="Grilled Chicken",
            calories=350.0, protein_g=30.0, carbs_g=10.0, fat_g=15.0,
            access_count=1,
        )

        self.client.post("/food/add_log/", {
            "food_name": "Grilled Chicken",
            "spoonacular_id": "716429",
        })

        # API should NOT have been called
        mock_get.assert_not_called()

        # Cache access_count should be incremented
        cache = NutritionCache.objects.get(spoonacular_id=716429)
        self.assertEqual(cache.access_count, 2)

        # Food log should have cached nutrition data
        log = FoodLog.objects.get(user=self.user, spoonacular_id=716429)
        self.assertEqual(log.calories, 350.0)
        self.assertEqual(log.protein_g, 30.0)

        # Metrics: 1 hit
        metrics = CacheMetrics.objects.get(date=date.today())
        self.assertEqual(metrics.cache_hits, 1)

    @patch("food.views.requests.get")
    def test_multiple_logs_build_metrics(self, mock_get):
        """Simulate realistic usage: 1 miss then 4 hits = 80% hit rate."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "calories": "200kcal", "protein": "5g", "carbs": "45g", "fat": "1g",
        }
        mock_get.return_value = mock_response

        # First log - cache miss
        self.client.post("/food/add_log/", {
            "food_name": "Brown Rice",
            "spoonacular_id": "55555",
        })

        # Next 4 logs - cache hits
        for _ in range(4):
            self.client.post("/food/add_log/", {
                "food_name": "Brown Rice",
                "spoonacular_id": "55555",
            })

        # API called only once
        self.assertEqual(mock_get.call_count, 1)

        # Cache access count = 5 (1 initial + 4 hits that increment)
        cache = NutritionCache.objects.get(spoonacular_id=55555)
        self.assertEqual(cache.access_count, 5)

        # Metrics: 80% hit rate
        metrics = CacheMetrics.objects.get(date=date.today())
        self.assertEqual(metrics.cache_hits, 4)
        self.assertEqual(metrics.cache_misses, 1)
        self.assertEqual(metrics.hit_rate, 80.0)
        self.assertEqual(metrics.api_calls_saved, 4)

    def test_no_spoonacular_id_skips_cache(self):
        """Foods without spoonacular_id should skip cache entirely."""
        self.client.post("/food/add_log/", {
            "food_name": "Custom Meal",
        })

        self.assertEqual(NutritionCache.objects.count(), 0)
        self.assertEqual(CacheMetrics.objects.count(), 0)
        log = FoodLog.objects.get(user=self.user, food_name="Custom Meal")
        self.assertIsNone(log.calories)


class CacheMetricsHelperTest(TestCase):
    def test_record_cache_hit_creates_and_increments(self):
        from food.views import _record_cache_hit
        _record_cache_hit()
        _record_cache_hit()
        _record_cache_hit()
        metrics = CacheMetrics.objects.get(date=date.today())
        self.assertEqual(metrics.cache_hits, 3)
        self.assertEqual(metrics.api_calls_saved, 3)
        self.assertEqual(metrics.cache_misses, 0)

    def test_record_cache_miss_creates_and_increments(self):
        from food.views import _record_cache_miss
        _record_cache_miss()
        _record_cache_miss()
        metrics = CacheMetrics.objects.get(date=date.today())
        self.assertEqual(metrics.cache_misses, 2)
        self.assertEqual(metrics.cache_hits, 0)
