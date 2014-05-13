# -*- coding: utf-8 -*-

import os
import re
import requests
import simplejson
from random import randint
from facepy import GraphAPI
from django.conf import settings
from django.contrib.auth.models import User
from django.template import loader

from social_reg_auth import constants

def create_inactive_user(username, password, email, first_name, last_name):
    new_user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=False
    )
    # Set password
    new_user.set_password(password)
    # Save
    new_user.save()
    return new_user


def generate_activation_code():
    """
    Generates a random activation code made up of 16 decimal digits
    """
    result = None
    while result is None:
        code = randint(
            constants.ACTIVATION_CODE_RANGE_START,
            constants.ACTIVATION_CODE_RANGE_END
        )
        try:
            # Checking if the code has already been used
            record = ActivationRecord.objects.get(code=code)
        except ActivationRecord.DoesNotExist:
            # Code is not used already so we can use it
            result = code
    return result


def create_activation_record(user):
    record = ActivationRecord(
        user=user,
        code=generate_activation_code()
    )
    record.save()
    return record


def check_password_minimal_stats(password):
    stats = {
        'total_length': 0,
        'letters': 0,
        'numbers': 0,
        'symbols': 0,
        'uppercase': 0,
        'lowercase': 0
    }

    password = password.strip()

    # Calculate stats
    stats['total_length'] = len(password)
    stats['letters'] = len([c for c in password if c.isalpha()])
    stats['numbers'] = len([c for c in password if c.isdigit()])
    stats['uppercase'] = len([c for c in password if c.isupper()])
    stats['lowercase'] = len([c for c in password if c.islower()])
    stats['symbols'] = len([c for c in password if \
                            (not c.isalpha() and not c.isdigit())])

    # Check for minimums
    if (stats['total_length'] < constants.PASSWORD_MIN_LENGTH or
        stats['letters'] < constants.PASSWORD_MIN_LETTERS or
        stats['numbers'] < constants.PASSWORD_MIN_NUMBERS or
        stats['symbols'] < constants.PASSWORD_MIN_SYMBOLS or
        stats['uppercase'] < constants.PASSWORD_MIN_UPPERCASE or
        stats['lowercase'] < constants.PASSWORD_MIN_LOWERCASE):
        return False
    else:
        return True

# Facebook stuff


def facebook_profile_picture_url(facebook_id):
    return ''.join([
        constants.FACEBOOK_BASE_GRAPH_API_URL,
        facebook_id,
        constants.FACEBOOK_PICTURE_SUFFIX,
    ])


def facebook_create_authorization_url(redirect_uri):
    return '%s?client_id=%s&redirect_uri=%s&scope=%s' % (
        constants.FACEBOOK_BASE_AUTH_URL,
        settings.FACEBOOK_APP_ID,
        redirect_uri,
        ','.join(constants.FACEBOOK_PERMISSIONS)
    )


def facebook_create_login_url(redirect_uri):
    return '%s?client_id=%s&redirect_uri=%s' % (
        constants.FACEBOOK_BASE_AUTH_URL,
        settings.FACEBOOK_APP_ID,
        redirect_uri
    )


def facebook_create_access_token_retrieval_url(redirect_uri, code):
    return '%s?client_id=%s&redirect_uri=%s&client_secret=%s&code=%s' % (
        constants.FACEBOOK_BASE_ATOKEN_URL,
        settings.FACEBOOK_APP_ID,
        redirect_uri,
        settings.FACEBOOK_APP_SECRET,
        code
    )


def facebook_get_access_token(redirect_uri, code):
    data = {}
    url = facebook_create_access_token_retrieval_url(redirect_uri, code)
    response = requests.get(url)
    try:
        json_response = simplejson.loads(response.content)
        return None
    except simplejson.JSONDecodeError:
        parts = response.content.split('|')
        for p in parts:
            sections = p.split('&')  # TODO: Improve
            for s in sections:
                k, v = s.split('=')
                data[k] = v
        if 'access_token' in data:
            return data['access_token']
        else:
            return None


def facebook_get_user_data(access_token):
    graph_api = GraphAPI(access_token)
    return graph_api.get('me')

def facebook_get_user_id_from_access_token(access_token):
    data = facebook_get_user_data(access_token)
    if 'id' in data:
        return data['id']
    else:
        return None

def facebook_get_registration_dict(access_token):
    results = {}
    data = facebook_get_user_data(access_token)

    # Direct mappings
    mapping = (
        ('first_name', 'first_name'),
        ('last_name', 'last_name'),
        ('username', 'username'),
        ('email', 'email'),
    )
    for data_field, registration_field in mapping:
        if data_field in data:
            results[registration_field] = data[data_field]

    # Manual mappings

    # Gender
    # if 'gender' in data and data['gender'] == 'male':
    #     results['gender'] = Account.GENDER_CHOICES.MALE
    # if 'gender' in data and data['gender'] == 'female':
    #     results['gender'] = Account.GENDER_CHOICES.FEMALE

    # Birthday
    # if 'birthday' in data:
    #     bday_regexp = '^([0-9]{2})\/([0-9]{2})/([0-9]{4})$'
    #     bday_match = re.search(bday_regexp, data['birthday'])
    #     if bday_match and len(bday_match.groups()) == 3:
    #         results['birthday'] = '%s/%s/%s' % (
    #             bday_match.group(2),
    #             bday_match.group(1),
    #             bday_match.group(3)
    #         )

    # Country
    # if 'location' in data and 'name' in data['location']:
    #     location_name = data['location']['name']
    #     location_parts = location_name.split(', ')
    #     if location_parts > 0:
    #         possible_country_name = location_parts[-1]
    #     for country_code, country_name in COUNTRIES:
    #         if possible_country_name == country_name:
    #             results['country'] = country_code

    if 'username' in results:
        results['userid']=results['username']


    results['email_confirmation'] = data['email']

    # Return result dictionary
    return results

# def facebook_picture_url_from_user_id(facebook_user_id):
#     return ''.join([
#         constants.FACEBOOK_BASE_GRAPH_API_URL,
#         facebook_user_id,
#         constants.FACEBOOK_PICTURE_SUFFIX,
#     ])

def facebook_get_user_fields(access_token):
    results = {}
    data = facebook_get_user_data(access_token)

    # Direct mappings
    mapping = (
        ('id', 'id'),
        ('name', 'name'),
        ('link', 'link'),
    )

    for data_field, registration_field in mapping:
        if data_field in data:
            results[registration_field] = data[data_field]

    # Add picture
    facebook_user_id = data['id']
    # results['picture'] = facebook_picture_url_from_user_id(facebook_user_id)

    # Return results
    return results

def create_facebook_user(user, access_token, fbdata=None):
    if fbdata is None and access_token is not None:
        fbdata = facebook_get_user_fields(access_token)
    if fbdata is not None:
        fuser = FacebookUser(
            user=user,
            facebook_user_id=fbdata['id'],
            name=fbdata['name'],
            link=fbdata['link'],
            oauth_access_token=access_token
        )
        fuser.save()
        return fuser
    else:
        return None
