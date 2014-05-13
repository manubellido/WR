# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.simple import direct_to_template
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings

from notifications.models import Notification
from user_profile.models import (UserProfile, UserFacebook, UserTwitter,
        UserFollower)
from user_profile.forms import UserProfileEditForm, AccountSettingsForm
from circuits.forms import make_categories_form
from circuits.models import (Circuit, CircuitRelatedUserProxy,
        CircuitCategoryFollow)


def show_activity(request):
    notifications = Notification.objects.filter(notified_user=request.user).\
        order_by('-created')
    return render(request,
                  'profile/activity.html',
                  {'notifications': notifications})
