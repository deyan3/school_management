from django.contrib import admin
from .models import Class

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'subject', 'teacher')
    search_fields = ('class_name', 'subject', 'teacher__name')
    # This enables 'Add Class' through Django Admin UI.

# If you already have other models, be sure to register them as needed.