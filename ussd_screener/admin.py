from django.contrib import admin

from .models import Option, Page, Session, Survey


class OptionAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    list_display = ('get_obj', 'get_pages', 'get_page_numbers')
    search_fields = ('number', 'text')

    def get_obj(self, obj):
        return obj

    def get_pages(self, obj):
        return ", ".join([p.text for p in obj.pages.all()])

    def get_page_numbers(self, obj):
        return ", ".join([p.page_num for p in obj.pages.all()])


class PageAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    list_display = ('text', 'page_num', 'parent_number')
    search_fields = ('text',)

    def parent_number(self, obj):
        if hasattr(obj.parent, 'page_num'):
            return obj.parent.page_num
        return obj.parent


class SurveyAdmin(admin.ModelAdmin):
    pass


class SessionAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    list_display = ('session_id', 'user', 'survey', 'prev_page_id')
    search_fields = ('user', 'survey')
    ordering = ('-created',)


admin.site.register(Option, OptionAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Session, SessionAdmin)
