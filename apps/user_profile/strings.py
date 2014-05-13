# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _


USER_PROFILE_USER = _(u'User')
USER_PROFILE_GENDER = _(u'Gender')
USER_PROFILE_HOMETOWN = _(u'Hometown')
USER_PROFILE_LANGUAGE = _(u'Language')
USER_PROFILE_INVITATIONS_LEFT = _(u'Available invitations')
USER_PROFILE_BIO = _(u'About me')
USER_PROFILE_AVATAR = _(u'Avatar')
USER_PROFILE_NAME = _(u'Username')
USER_PROFILE_VERBOSE_NAME = _(u'User profile')
USER_PROFILE_VERBOSE_NAME_PLURAL = _(u'User profiles')
# Missing translations here
USER_PROFILE_IS_ORGANIZATION = _('Has organization data')

PASSWORD_FORM_OLD_PASSWORD = _(u'Current Password')
PASSWORD_FORM_NEW_PASSWORD = _(u'New Password')
PASSWORD_FORM_NEW_PASSWORD_AGAIN = _(u'New Password (Again)')

GENDER_MALE = _(u'Male')
GENDER_FEMALE = _(u'Female')
GENDER_UNDISCLOSED = _(u'Prefer not to say')

USER_FACEBOOK_USER = _(u'Usuario')
USER_FACEBOOK_ACCESS_TOKEN = _(u'Access Token para Facebook')
USER_FACEBOOK_GRAPHID = _(u'Facebook ID')
USER_FACEBOOK_NAME = _(u'Facebook name')
USER_FACEBOOK_LINK = _(u'Facebook link')
USER_FACEBOOK_VERBOSE_NAME = _(u'Facebook user credentials')
USER_FACEBOOK_VERBOSE_NAME_PLURAL = _(u'Facebook user credentials')

USER_TWITTER_USER = _('User')
USER_TWITTER_USER_ID = _('Twitter ID')
USER_TWITTER_NAME = _('Twitter name')
USER_TWITTER_OAUTH_TOKEN = _(u'Twitter OAuth Token')
USER_TWITTER_OAUTH_SECRET = _(u'Twitter OAuth Secret')
USER_TWITTER_SCREEN_NAME = _(u'Twitter user name')
USER_TWITTER_VERBOSE_NAME = _(u'Twitter user credentials')
USER_TWITTER_VERBOSE_NAME_PLURAL = _(u'Twitter user credentials')

USER_FOURSQUARE_USER = _('User')
USER_FOURSQUARE_USER_ID = _('Foursquare ID')
USER_FOURSQUARE_NAME = _('Foursquare name')
USER_FOURSQUARE_ACCESS_TOKEN = _(u'Foursquare OAuth access token')
USER_FOURSQUARE_LINK = _(u'Foursquare link')
USER_FOURSQUARE_VERBOSE_NAME = _(u'Foursquare user credentials')
USER_FOURSQUARE_VERBOSE_NAME_PLURAL = _(u'Foursquare user credentials')

USER_FOLLOWER_VERBOSE_NAME = _(u'User follower')
USER_FOLLOWER_VERBOSE_NAME_PLURAL = _(u'User followers')

USER_FOLLOWER_OWNER = _(u'Owner')
USER_FOLLOWER_FOLLOWER = _(u'Follower')
USER_FOLLOWER_CONTEXT = _(u'Context')

FC_UNSPECIFIED = _(u'Unspecified context')
FC_RECIPROCAL = _(u'Reciprocal user')
FC_SPONTANEOUS = _(u'Spontaneous follower')
FC_FACEBOOK_SUGGESTION = _(u'Facebook friend suggestion')
FC_TWITTER_SUGGESTION = _(u'Twitter friend suggestion')
FC_WORLDRAT_SUGGESTION = _(u'Worldrat suggestion')

USER_FOLLOWER_VALIDATION_SELF = _(u'User can not follow himself')
USER_FACEBOOK_VERBOSE_NAME = _(u'Facebook user credential')
USER_FACEBOOK_VERBOSE_NAME_PLURAL = _(u'Facebook user credentials')
USER_TWITTER_VERBOSE_NAME = _(u'Twitter user crendential')
USER_TWITTER_VERBOSE_NAME_PLURAL = _(u'Twitter user credentials')

# FACEBOOK EMAILING
EMAIL_ACCOUNT_CREATED_FB_SUBJECT = _(u'Welcome to Worldrat')
EMAIL_ACCOUNT_CREATED_FB_CONTENT = _(u'We have created an account for\
 you using your social data. You can continue login in with \
Facebook/Twitter, but just so you know your Worldrat credentials are:\n \
    username: %(username)s\n \
    password: %(password)s\n \
We recommend you change your password to something you remember. '
)

# API

NON_EXISTANT_USER = _(
    u'No user exists under the specified identifier.'
)

NON_EXISTANT_FOLLOWER = _(
    u'No user exists under the specified follower identifier.'
)

NON_EXISTANT_FOLLOWEE = _(
    u'No user exists under the specified followee identifier.'
)

NON_EXISTANT_FOLLOWER_PROFILE = _(
    u'The follower does not yet have a user profile created.'
)

NON_EXISTANT_FOLLOWEE_PROFILE = _(
    u'The followee does not yet have a user profile created.'
)

ALREADY_FOLLOWING_USER = _(
    u'Already following user'
)

ALREADY_NOT_FOLLOWING_USER = _(
    u'Already not following user'
)

SELF_FOLLOW_ERROR = _(
    u'A user account can not follow itself'
)

EMAIL_ALREADY_USED = _(
    u'The email %(email)s is already being used '
    u'by another user.'
)

VALID_EMAIL = _(
    u'This mail is valid.'
)

INVALID_EMAIL = _(
    u'The email %(email)s is invalid.'
)
NO_EMAIL = _(u'You did not specify an email')

WELCOME_MESSAGE = _(u'Welcome to Worldrat, where rat is you!')
