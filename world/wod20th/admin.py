# world/wod20th/admin.py
from django.contrib import admin
from .models import Stat

@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_line', 'category', 'stat_type')
    search_fields = ('name', 'game_line', 'category', 'stat_type')
