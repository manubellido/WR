# -*- coding: utf-8 -*-

from django.contrib import admin
from circuits.models import Circuit, CircuitStop, Topic
from circuits import constants

class CircuitAdmin(admin.ModelAdmin):
    list_display = ('name','description','category','category_dropdown')
    class Media:
        js = ('/static/js/inline_admin.js','')

    def category_dropdown(self,obj):
        #Cheap Way to generate the dropdown
        content = '<select class="inline-admin-category-edit" data-id="%s">'
        content = content % obj.id
        for option in constants.CIRCUIT_CATEGORY_CHOICES:
            print type(obj.category)
            print option[0]==obj.category
            if obj.category == option[0]:
                selected = 'selected="selected"'
            else:
                selected = ''
            content += '<option %s value="%s">%s</option>' % (
                    selected,
                    option[0],
                    unicode(option[1])
                    )
        content += '</select>'
        return content
    category_dropdown.allow_tags = True

admin.site.register(Circuit,CircuitAdmin)
admin.site.register(Topic)
admin.site.register(CircuitStop)
