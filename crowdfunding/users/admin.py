from django.contrib import admin
from .models import CustomUser, UserChangeLog

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']
    fieldsets = (
        ('Основная информация', {
            'fields': ('username', 'email', 'first_name', 'last_name')
        }),
        ('Статус', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Даты', {
            'fields': ('date_joined', 'last_login')
        }),
    )

@admin.register(UserChangeLog)
class UserChangeLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'changed_by', 'field_name', 'old_value', 'new_value', 'changed_at']
    list_filter = ['changed_at', 'field_name', 'changed_by']
    search_fields = ['user__username', 'changed_by__username']
    readonly_fields = ['user', 'changed_by', 'field_name', 'old_value', 'new_value', 'changed_at']
    ordering = ['-changed_at']

    def has_add_permission(self, request):
        return False  # Запретить ручное добавление логов

    def has_delete_permission(self, request, obj=None):
        return False  # Запретить удаление логов
