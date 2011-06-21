from django.contrib import admin
from django.contrib.comments.admin import CommentsAdmin
from django.contrib.comments.models import Comment

from blog import views
from blog.models import Tag, Entry, Link


class TagAdmin(admin.ModelAdmin):
    list_display = ['slug', 'title']


class EntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'status', 'pub_date', 'is_popular']
    list_editable = ['is_popular']
    prepopulated_fields = {'slug': ['title']}


class LinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'pub_date']


def report_spam_and_delete(modeladmin, request, queryset):
    for comment in queryset:
        views.report_spam_and_delete(comment)


class CommentsAdminWithSpamReporting(CommentsAdmin):
    actions = CommentsAdmin.actions + [report_spam_and_delete]


admin.site.register(Tag, TagAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.unregister(Comment)
admin.site.register(Comment, CommentsAdminWithSpamReporting)
