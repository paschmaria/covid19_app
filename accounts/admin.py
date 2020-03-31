from django.contrib import admin

from .models import HealthStatus, User, USSDUser


class HealthStatusAdmin(admin.ModelAdmin):
    # list_display = ('risk_level',)
    search_fields = ('primary_contact', 'secondary_contact')

    def risk_level(self):
        pass

class UserAdmin(admin.ModelAdmin):
    pass

class USSDUserAdmin(admin.ModelAdmin):
    pass


admin.site.register(HealthStatus, HealthStatusAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(USSDUser, USSDUserAdmin)
