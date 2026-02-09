from django.contrib import admin
from django.utils.html import format_html
from .models import NutritionCache, CacheMetrics


@admin.register(NutritionCache)
class NutritionCacheAdmin(admin.ModelAdmin):
    list_display = ('spoonacular_id', 'food_name', 'calories', 'access_count', 'last_accessed')
    list_filter = ('created_at',)
    search_fields = ('food_name', 'spoonacular_id')
    ordering = ('-access_count',)
    readonly_fields = ('created_at', 'last_accessed', 'access_count', 'raw_api_response')
    actions = ['clear_cache_entries']

    @admin.action(description="Clear selected cache entries")
    def clear_cache_entries(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Cleared {count} cache entries.")


@admin.register(CacheMetrics)
class CacheMetricsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_requests_display', 'cache_hits', 'cache_misses', 'hit_rate_display')
    ordering = ('-date',)
    readonly_fields = ('date', 'cache_hits', 'cache_misses', 'api_calls_saved')

    def total_requests_display(self, obj):
        return obj.total_requests
    total_requests_display.short_description = 'Total Requests'

    def hit_rate_display(self, obj):
        rate = obj.hit_rate
        if rate >= 70:
            color = '#28a745'
        elif rate >= 50:
            color = '#fd7e14'
        else:
            color = '#dc3545'
        return format_html('<span style="color: {}; font-weight: bold;">{}%</span>', color, rate)
    hit_rate_display.short_description = 'Hit Rate'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
