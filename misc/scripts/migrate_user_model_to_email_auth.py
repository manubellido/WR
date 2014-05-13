# -*- coding: utf-8 -*-

from user_profile.models import User, UserEmail

if __name__ == "__main__":
    for user in User.objects.all():
        user_email = UserEmail(email=user.email)
        user_email.user = user
        user_email.verified=True
        user_email.save()
