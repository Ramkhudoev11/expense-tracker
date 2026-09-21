from django.contrib import admin
from .models import Category, Expense, Subscription, ScheduleItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'date']
    list_filter = ['category', 'date']
    search_fields = ['description']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'current_period_end']
    list_filter = ['is_active']
    search_fields = ['user__username']

from .models import ScheduleItem

@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'time', 'title']
    list_filter = ['user']