from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import Post, Group, Comment


class EditLinkToInlineObject(object):
    def edit_link(self, instance):
        app_label = instance._meta.app_label
        model_name = instance._meta.model_name
        path = f'admin:{app_label}_{model_name}_change'
        url = reverse(path,  args=[instance.pk])
        if instance.pk:
            return mark_safe(u'<a href="{u}">Редактировать</a>'.format(u=url))
        else:
            return ''


class PostInline(EditLinkToInlineObject, admin.TabularInline):
    model = Post
    readonly_fields = ('edit_link', )


class CommentInline(EditLinkToInlineObject, admin.TabularInline):
    model = Comment
    readonly_fields = ('edit_link', )


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = (
        'group',
    )
    search_fields = (
        'text',
    )
    list_filter = (
        'pub_date',
    )
    empty_value_display = '-пусто-'
    inlines = (CommentInline, )


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'description'
    )
    search_fields = (
        'description',
    )
    empty_value_display = '-пусто-'
    inlines = (PostInline, )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'post'
    )
    search_fields = (
        'text',
    )
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
