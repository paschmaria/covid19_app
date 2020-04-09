from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import HealthStatus, User, USSDUser


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'email_confirmed', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_staff', 'is_superuser'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)


class HealthStatusAdmin(admin.ModelAdmin):
    search_fields = ('primary_contact', 'secondary_contact')


class USSDUserAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = ('phone_number', 'language', 'state', 'lga')
    search_fields = ('phone_number', 'language')
    date_hierarchy = 'created'
    ordering = ('-created',)


admin.site.register(HealthStatus, HealthStatusAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(USSDUser, USSDUserAdmin)
