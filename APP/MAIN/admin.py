from django.contrib import admin
from django.contrib.auth.models import User
from .models import *

# Register your models here.

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['app_name', 'author', 'created', 'updated']
    search_fields = ['app_name']
    ordering = ['created']
    list_filter = ['app_name', 'author']


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ['email']
    ordering = ['email']
    list_filter = ['email']


@admin.register(Pm)
class PmAdmin(admin.ModelAdmin):
    list_display = ['email']
    ordering = ['email']
    list_filter = ['email']




@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['email']
