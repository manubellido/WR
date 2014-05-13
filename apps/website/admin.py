# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


admin.site.unregister(User)


class CustomUserAdmin(UserAdmin):
    list_display = ('id',) + UserAdmin.list_display
    readonly_fields = ('id',)
    fieldsets =  UserAdmin.fieldsets
    fieldsets[0][1]['fields'] = ('id',) + fieldsets[0][1]['fields']

admin.site.register(User, CustomUserAdmin)
