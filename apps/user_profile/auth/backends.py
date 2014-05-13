# -*- coding: utf-8 -*-

from django.contrib.auth.models import User, check_password


class EmailAuthentication(object):
    def get_user(user_id):
        if User.objects.filter(username=name).exists():
            user = User.objects.get(username=name)
            return User
        elif UserEmail.objects.filter(email=user_id).exists():
            email = UserEmail.objects.get(email=user_id)
            return email.user
        else:
            return None


    @classmethod
    def authenticate(cls, handle=None, password=None):
        """
        later *args and **kwargs
        """
        if handle:
            user = cls.get_user(user_id)
            if user:
                if user.check_password(password):
                    return user
        return None
