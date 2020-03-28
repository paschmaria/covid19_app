from django.contrib import admin

from .models import Option, Page, Survey, Session


class OptionAdmin(admin.ModelAdmin):
    pass

class PageAdmin(admin.ModelAdmin):
    pass

class SurveyAdmin(admin.ModelAdmin):
    pass

class SessionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Option, OptionAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Session, SessionAdmin)