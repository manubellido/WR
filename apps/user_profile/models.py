# -*- coding: utf-8 -*-

import random
from ordereddict import OrderedDict
from sorl.thumbnail.fields import ImageField
from unidecode import unidecode
import hashlib
from numconv import NumConv

from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.gis.db import models
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.conf import settings

from common.models import AuditableModel
from common.datastructures import Enumeration
from common.utils.pictures import uuid_based_picture_name
from circuits.models import Circuit
from user_profile import strings, constants
from organizations.models import Organization
import user_profile.settings


class UserProfile(AuditableModel):

    GENDER_CHOICES = Enumeration([
        (1, 'MALE', strings.GENDER_MALE),
        (2, 'FEMALE', strings.GENDER_FEMALE),
        (3, 'UNDISCLOSED', strings.GENDER_UNDISCLOSED)
    ])

    user = models.OneToOneField(User,
        verbose_name=strings.USER_PROFILE_USER,
    )

    gender = models.PositiveIntegerField(
        verbose_name=strings.USER_PROFILE_GENDER,
        choices=GENDER_CHOICES,
        default=3,
    )

    hometown = models.CharField(
        verbose_name=strings.USER_PROFILE_HOMETOWN,
        max_length=75,
        blank=True,
        default=u'Lima, Perú',
    )

    language = models.PositiveIntegerField(
        verbose_name=strings.USER_PROFILE_LANGUAGE,
        choices=constants.LANGUAGE_CHOICES,
        default=1
    )

    invitations_left = models.PositiveIntegerField(
        verbose_name=strings.USER_PROFILE_INVITATIONS_LEFT,
        default=settings.CLOSED_BETA_DEFAULT_ADDITIONAL_INVITATIONS
    )

    # a User can have circuits as favorites
    favorites = models.ManyToManyField(Circuit,
        related_name='follower_profiles',
    )

    bio = models.TextField(
        verbose_name=strings.USER_PROFILE_BIO,
        blank=True,
    )

    picture = ImageField(
        verbose_name=strings.USER_PROFILE_AVATAR,
        upload_to=uuid_based_picture_name('pictures/users'),
        blank=True,
        null=True,
    )

    # Organization data
    is_organization = models.BooleanField(
        verbose_name=strings.USER_PROFILE_IS_ORGANIZATION,
        default=False
    )

    def __unicode__(self):
        return u'%s' % (self.user.get_full_name(),)

    class Meta:
        verbose_name = strings.USER_PROFILE_VERBOSE_NAME
        verbose_name_plural = strings.USER_PROFILE_VERBOSE_NAME_PLURAL

    @staticmethod
    def get_or_create(email, first, last, fb_id):
        """logs a user if email dont exists, or creates a user logs
        in if email is in use"""
        from common.utils.verbose_password_generator import pass_generator
        
        # email exists is our database
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
        # email is new to our database so create a user and login
        else:
            psw = pass_generator()
            user = UserProfile.create_user_with_tokens(
                first=first,
                last=last,
                email=email,
                password=psw
            )
            fb_profile = UserFacebook(
                user=user,
                name=first+' '+last,
                facebook_graphid=fb_id,
            )
            fb_profile.save()
        return user


    @staticmethod
    def create_user_with_tokens(
        first,
        last,
        email,
        password,
        username=None,
        facebook_oauth_token=None,
        facebook_graphid=None,
        twitter_oauth_token=None,
        twitter_oauth_secret=None
    ):
        """
        method for creating a user, bind to userprofile and bind to
        twitter and facebook profiles if needed
        """
        from django.core.mail import EmailMultiAlternatives

        #Check that email is not already in use
        if User.objects.filter(email=email).exists():
            return None

        # create a hash from email in order to be used as username
        username = str(hashlib.sha1(email).hexdigest())
        username = NumConv(16).str2int(username)
        username = NumConv(64).int2str(username)

        # create a new User
        new_user = User.objects.create_user(
            username,
            email,
            password
        )
        new_user.first_name = (first)
        new_user.last_name = (last)
        new_user.save()
        # bind new_user to a UserProfile
        new_profile = UserProfile(user=new_user)
        new_profile.save()
        # bind to Twitter account if comes
        if twitter_oauth_token is not None:
            tw = UserTwitter(user=new_user,
                oauth_token_key=twitter_oauth_token,
                oauth_token_secret=twitter_oauth_secret,
                screen_name=username,
            )
            tw.save()
        # bind to facebook if comes
        if facebook_oauth_token is not None:
            fb = UserFacebook(user=new_user,
                facebook_access_token=facebook_oauth_token,
                facebook_graphid=facebook_graphid
            )
            fb.save()

        #send an email to user with its password, and indications
        # to change it and that he can continue to log in with 
        # facebook
        #       mandatory fields
        subject = strings.EMAIL_ACCOUNT_CREATED_FB_SUBJECT
        to =  new_user.email
        from_email = settings.DEFAULT_FROM_EMAIL
        # get text version of the message
        text_content = strings.EMAIL_ACCOUNT_CREATED_FB_CONTENT % {
            'username':new_user.email, 'password':password
        }
        #       FIXME: HTML version implementation pending
        # html_content = self.get_email_content_from_type(
        #     self.notification_type
        # )
        msg = EmailMultiAlternatives(
            subject, 
            text_content,
            from_email,
            [to]
        )
        #msg.attach_alternative(html_content, "text/html")
        msg.send()

        return new_user

    def save_image_from_url(self, url):
        """Store image locally from url"""
        import urllib
        import os
        from django.core.files import File
        result = urllib.urlretrieve(url)
        self.picture.save(
                os.path.basename(url),
                File(open(result[0]))
                )
        self.save()

    def is_following(self, user):
        if UserFollower.objects.filter(
                owner=user).filter(follower=self.user).count() > 0:
            return True
        else:
            return False

    def is_follower(self, user):
        if UserFollower.objects.filter(
                owner=self.user).filter(follower=user).count() > 0:
            return True
        else:
            return False

    def follow(self, user):
        if self.user == user:
            return False
        if self.is_following(user):
            return False
        else:
            record = UserFollower(owner=user, follower=self.user)
            record.save()
            return True

    def unfollow(self, user):
        if self.user == user:
            return False
        try:
            record = UserFollower.objects.get(owner=user, follower=self.user)
            record.delete()
            return True
        except UserFollower.DoesNotExist:
            return False

    def add_follower(self, user):
        if self.user == user:
            return False
        if self.is_follower(user):
            return False
        else:
            record = UserFollower(owner=self.user, follower=user)
            record.save()
            return True

    def remove_follower(self, user):
        if self.user == user:
            return False
        try:
            record = UserFollower.objects.get(owner=self.user, follower=user)
            record.delete()
            return True
        except UserFollower.DoesNotExist:
            return False

    def get_followers(self):
        if hasattr(self.user, 'follower_records_as_owner'):
            records = self.user.follower_records_as_owner.all()
            user_id_list = [record.follower.id for record in records]
            return User.objects.filter(
                id__in=user_id_list
            ).order_by('username')
        else:
            return User.objects.none()

    def get_followed_users(self):
        if hasattr(self.user, 'follower_records_as_follower'):
            records = self.user.follower_records_as_follower.all()
            user_id_list = [record.owner.id for record in records]
            return User.objects.filter(
                id__in=user_id_list
            ).order_by('username')
        else:
            return User.objects.none()

    def get_restful_link_metadata(self, rel='alternate'):
        metadata = OrderedDict()
        metadata['href'] = self.get_restful_url()
        metadata['rel'] = rel
        metadata['title'] = self.user.get_full_name()
        metadata['type'] = 'application/json'
        return metadata

    def get_restful_url(self):
        return "%s%s" % (
            settings.API_V1_PREFIX.rstrip('/'),
            reverse('user_resource', kwargs={'user_id': self.user.pk})
        )


class UserFacebook(AuditableModel):
    user = models.OneToOneField(User,
        verbose_name=strings.USER_FACEBOOK_USER,
        related_name='facebook_data'
    )

    oauth_access_token = models.CharField(
        verbose_name=strings.USER_FACEBOOK_ACCESS_TOKEN,
        max_length=128,
        null=True,
        blank=True
    )

    facebook_graphid = models.CharField(
        verbose_name=strings.USER_FACEBOOK_GRAPHID,
        max_length=20
    )

    name = models.CharField(
        verbose_name=strings.USER_FACEBOOK_NAME,
        max_length=128
    )

    link = models.URLField(
        verbose_name=strings.USER_FACEBOOK_LINK,
        verify_exists=False
    )

    class Meta:
        verbose_name = strings.USER_FACEBOOK_VERBOSE_NAME
        verbose_name_plural = strings.USER_FACEBOOK_VERBOSE_NAME_PLURAL

    def __repr__(self):
        if self.id:
            return u'<Facebook User #%d: "%s">' % (
                self.id,
                unidecode(self.name),
            )
        else:
            return u'<Account "%s (%s)">' % (
                unidecode(self.name),
                self.facebook_user_id
            )

    def __unicode__(self):
        return self.link


class UserTwitter(AuditableModel):

    user = models.OneToOneField(User,
        verbose_name=strings.USER_TWITTER_USER,
        related_name='twitter_data'
    )

    twitter_user_id = models.CharField(
        verbose_name=strings.USER_TWITTER_USER_ID,
        max_length=32
    )

    name = models.CharField(
        verbose_name=strings.USER_TWITTER_NAME,
        max_length=128
    )

    oauth_token_key = models.CharField(
        verbose_name=strings.USER_TWITTER_OAUTH_TOKEN,
        max_length=128,
        null=True,
        blank=True
    )

    oauth_token_secret = models.CharField(
        verbose_name=strings.USER_TWITTER_OAUTH_SECRET,
        max_length=128,
        null=True,
        blank=True
    )

    screen_name = models.CharField(
        verbose_name=strings.USER_TWITTER_SCREEN_NAME,
        max_length=30,
        unique=True
    )

    link = models.URLField(
        verbose_name=strings.USER_FACEBOOK_LINK,
        verify_exists=False
    )

    class Meta:
        verbose_name = strings.USER_TWITTER_VERBOSE_NAME
        verbose_name_plural = strings.USER_TWITTER_VERBOSE_NAME_PLURAL


class UserFoursquare(AuditableModel):

    user = models.OneToOneField(User,
        verbose_name=strings.USER_FOURSQUARE_USER,
        related_name='foursquare_data'
    )

    foursquare_user_id = models.CharField(
        verbose_name=strings.USER_FOURSQUARE_USER_ID,
        max_length=32
    )

    name = models.CharField(
        verbose_name=strings.USER_FOURSQUARE_NAME,
        max_length=128
    )

    oauth_access_token = models.CharField(
        verbose_name=strings.USER_FOURSQUARE_ACCESS_TOKEN,
        max_length=128,
        null=True,
        blank=True
    )

    link = models.URLField(
        verbose_name=strings.USER_FOURSQUARE_LINK,
        verify_exists=False
    )

    class Meta:
        verbose_name = strings.USER_FOURSQUARE_VERBOSE_NAME
        verbose_name_plural = strings.USER_FOURSQUARE_VERBOSE_NAME_PLURAL


class UserFollower(AuditableModel):
    """
    Relation between user and user, friendship-like relation
    """

    FOLLOWER_CONTEXT_CHOICES = Enumeration([
        (1, 'UNSPECIFIED', strings.FC_UNSPECIFIED),
        (1, 'SPONTANEOUS', strings.FC_SPONTANEOUS),
        (2, 'RECIPROCAL', strings.FC_RECIPROCAL),
        (3, 'FACEBOOK_SUGGESTION', strings.FC_FACEBOOK_SUGGESTION),
        (4, 'TWITTER_SUGGESTION', strings.FC_TWITTER_SUGGESTION),
        (5, 'WORLDRAT_SUGGESTION', strings.FC_WORLDRAT_SUGGESTION),
    ])

    owner = models.ForeignKey(User,
        verbose_name=strings.USER_FOLLOWER_OWNER,
        related_name='follower_records_as_owner'
    )

    follower = models.ForeignKey(User,
        verbose_name=strings.USER_FOLLOWER_FOLLOWER,
        related_name='follower_records_as_follower'
    )

    context = models.PositiveIntegerField(
        verbose_name=strings.USER_FOLLOWER_CONTEXT,
        default=FOLLOWER_CONTEXT_CHOICES.UNSPECIFIED
    )

    class Meta:
        verbose_name = strings.USER_FOLLOWER_VERBOSE_NAME
        verbose_name_plural = strings.USER_FOLLOWER_VERBOSE_NAME_PLURAL
        unique_together = (('owner', 'follower'),)

    def __unicode__(self):
        return u'%s follows %s' % (self.follower, self.owner)

    def clean(self):
        if self.user == self.follower:
            raise ValidationError(strings.USER_FOLLOWER_VALIDATION_SELF)


class EmailManager(models.Manager):
    """
    Manager to return only active emails
    """
    def activated(self):
        return super(EmailManager, self).get_query_set().filter(verified=True)


class UserEmail(models.Model):
    """
    """

    email = models.EmailField(unique=True)
    verification_code = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True
    )
    verified = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='emails')

    objects = EmailManager()

    def __unicode__(self):
        return u'%s: %s' % (self.email, self.verified)


    def verify_email(self, verification_code):
        """
        If verification code matches mark email as verified.
        Return the result of the operation
        """
        if self.verification_code == verification_code:
            self.activated = True
            self.save()
            return True
        else:
            return False
        

    def generate_verification_code(self):
        """
        Generate a verification code for an email.
        The verification must be unique.
        Returns the code.
        """
        
        while True:
            code = random.randint(
                constants.REGISTRATION_CODE_RANGE_START,
                constants.REGISTRATION_CODE_RANGE_START,
                )
            
            self.verification_code = code
            try:
                self.save()
                break
            except ValidationError:
                pass

        return code

    def verification_url(self):
        return reverse('verify_user_email', kwargs={
                'verification_code': self.verification_code,
                })

    def send_verification_email(self):
        """
        Regenerate verification code and send email
        """

        code = self.generate_verification_code()

        message = render_to_string(
            template_name='registration/verification_email.txt',
            dictionary={'user_email': self,},
            )

        send_mail(
            subject=user_profile.settings.VERIFICATION_MAIL_SUBJECT,
            message=message,
            from_email=settings.EMAIL_DEFAULT_FROM_VALUE,
            recipient_list=[self.email],
            )
