from django.contrib import admin

from .models import Option, Page, Session, Survey, SurveyResponse


class OptionAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    list_display = ('get_obj', 'get_pages', 'get_page_numbers')
    search_fields = ('number', 'text')
    raw_id_fields = ('pages',)

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
    raw_id_fields = ('parent',)
    save_as = True

    def parent_number(self, obj):
        if hasattr(obj.parent, 'page_num'):
            return obj.parent.page_num
        return obj.parent


class SurveyAdmin(admin.ModelAdmin):
    pass


class SurveyResponseAdmin(admin.ModelAdmin):
    pass


class SessionAdmin(admin.ModelAdmin):
    actions_on_bottom = True
    list_per_page = 50
    list_display = ('session_id', 'created', 'user', 'survey')
    search_fields = ('user', 'survey')
    date_hierarchy = 'created'
    raw_id_fields = ('user',)
    ordering = ('-created',)


admin.site.register(Option, OptionAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(SurveyResponse, SurveyResponseAdmin)
admin.site.register(Session, SessionAdmin)
