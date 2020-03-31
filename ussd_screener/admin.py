from django.contrib import admin

from .models import Option, Page, Survey, Session


class OptionAdmin(admin.ModelAdmin):
    list_display = ('get_obj', 'get_pages', 'get_page_numbers')
    search_fields = ('number', 'text')

    def get_obj(self, obj):
        return obj

    def get_pages(self, obj):
        return ", ".join([p.text for p in obj.pages.all()])

    def get_page_numbers(self, obj):
        return ", ".join([p.page_num for p in obj.pages.all()])

class PageAdmin(admin.ModelAdmin):
    list_display = ('text', 'page_num', 'parent')
    search_fields = ('text',)

class SurveyAdmin(admin.ModelAdmin):
    pass

class SessionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Option, OptionAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Session, SessionAdmin)