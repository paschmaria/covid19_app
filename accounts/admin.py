from django.contrib import admin

from .models import User, USSDUser


class UserAdmin(admin.ModelAdmin):
    pass

class USSDUserAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, USSDUserAdmin)
admin.site.register(USSDUser, USSDUserAdmin)
