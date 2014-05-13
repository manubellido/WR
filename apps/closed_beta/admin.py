# -*- coding: utf-8 -*-

from django.contrib import admin
from closed_beta.models import Invitation
from closed_beta import strings

def invitation_approve_action(modeladmin, request, queryset):
    for invitation in queryset:
        invitation.approve(sender=request.user)

invitation_approve_action.short_description = strings.INVITATION_APPROVE_ACTION

class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'approved', 'used',)
    readonly_fields = ('mail_sent', 'used', 'ipaddr', 'email',)
    list_filter = ('approved' , 'used',)
    actions = (invitation_approve_action,)


admin.site.register(Invitation, InvitationAdmin)
