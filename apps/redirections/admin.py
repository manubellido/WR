# -*- coding: utf-8 -*-
from django.contrib import admin

from redirections.models import Redirection


class RedirectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'redirect_to',)
    search_fields = ('name', 'path', 'redirect_to',)

admin.site.register(Redirection, RedirectionAdmin)
