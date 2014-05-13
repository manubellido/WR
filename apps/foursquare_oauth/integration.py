# -*- coding: utf-8 -*-

import re
import requests
import simplejson

from django.core.urlresolvers import reverse
from django.conf import settings
import foursquare

import user_profile.strings as strings
from user_profile.integration import OAuthIntegrator
from user_profile.models import UserFoursquare
from user_profile.utils import retrieve_image_as_base_64
from django_countries.countries import COUNTRIES


class FoursquareIntegrator(OAuthIntegrator):

    def get_oauth_client_id(self):
        return settings.FS_CLIENT_ID

    def get_oauth_secret(self):
        return settings.FS_CLIENT_SECRET

    def make_foursquare_client(self, redirect_uri=None):
        return foursquare.Foursquare(
            client_id=self.get_oauth_client_id(),
            client_secret=self.get_oauth_secret(),
            redirect_uri=redirect_uri
        )


    def create_authorization_url(self, redirect_uri):
        return '%s?client_id=%s&response_type=code&redirect_uri=%s' % (
            self.get_base_authorization_url(),
            self.get_oauth_client_id(),
            redirect_uri,
        )

    def get_base_authorization_url(self):
        return 'https://www.foursquare.com/oauth2/authenticate'

    #Not yet implemented
    def get_base_access_token_retrieval_url(self):
        return 'https://graph.facebook.com/oauth/access_token'

    #Not yet implemented
    def get_base_user_information_url(self):
        return 'https://graph.facebook.com/me'
    
    #Not yet implemented
    def get_profile_picture_url(self,id):
        return ''.join([
            'http://graph.facebook.com/',
            id,
            '/picture',
        ])
    def get_full_registration_end_url(self):
        return ''.join([
            settings.REDIRECTOR_PREFIX,
            '/foursquare'
        ])

    #Not yet implemented
    def get_full_login_end_url(self):
        return ''.join([
            settings.SITE_PREFIX,
            reverse('facebook_login_redirection_end')
        ])

    #Not yet implemented
    def get_user_information_url(self, access_token, fields=None):
        result = '%s?access_token=%s' % (
            self.get_base_user_information_url(),
            access_token
        )
        if fields:
            field_list = ','.join(fields)
            result = result + '&fields=%s' % field_list
        return result

    def get_access_token(self, redirect_uri, code):
        client = self.make_foursquare_client(redirect_uri=redirect_uri)
        access_token = client.oauth.get_token(code)
        return access_token

    #Not yet implemented
    def get_user_information_as_json(self, access_token, fields=None):
        url = self.get_user_information_url(access_token, fields)
        response = requests.get(url)
        return simplejson.loads(response.content)

    #Not yet implemented
    def get_user_picture(self, access_token):
        fields = ('picture', )
        data = self.get_user_information_as_json(access_token, fields)
        return data.get('picture', None)

    #Not yet implemented
    def get_registration_fields(self, access_token):
        results = {}
        data = self.get_user_information_as_json(access_token)

        # Direct mappings
        mapping = (
            ('first_name', 'firstname'),
            ('last_name', 'lastname'),
            ('username', 'username'),
            ('email', 'email'),
        )
        for data_field, registration_field in mapping:
            if data_field in data:
                results[registration_field] = data[data_field]

        # Manual mappings

        # Gender
        if 'gender' in data and data['gender'] == 'male':
            results['gender'] = strings.GENDER_MALE
        if 'gender' in data and data['gender'] == 'female':
            results['gender'] = strings.GENDER_FEMALE

        # Birthday
        if 'birthday' in data:
            bday_regexp = '^([0-9]{2})\/([0-9]{2})/([0-9]{4})$'
            bday_match = re.search(bday_regexp, data['birthday'])
            if bday_match and len(bday_match.groups()) == 3:
                results['birthday'] = '%s/%s/%s' % (
                    bday_match.group(2),
                    bday_match.group(1),
                    bday_match.group(3)
                )

        # Country
        if 'location' in data and 'name' in data['location']:
            location_name = data['location']['name']
            location_parts = location_name.split(', ')
            if location_parts > 0:
                possible_country_name = location_parts[-1]
            for country_code, country_name in COUNTRIES:
                if possible_country_name == country_name:
                    results['country'] = country_code

        if 'username' in results:
            results['userid']=results['username']

        # Return result dictionary
        return results

    #Not yet implemented
    def get_account_extra_fields(self, access_token):
        results = {}
        data = self.get_user_information_as_json(access_token)

        # Direct mappings
        mapping = (
            ('bio', 'bio'),
            ('website', 'website'),
        )

        for data_field, registration_field in mapping:
            if data_field in data:
                results[registration_field] = data[data_field]

        # Manual mappings
        picture_url = self.get_user_picture(access_token)

        if picture_url:
            results['picture'] = picture_url
        # Return results
        return results

    #Not yet implemented
    def get_facebook_user_fields(self, access_token):
        results = {}
        data = self.get_user_information_as_json(access_token)

        # Direct mappings
        mapping = (
            ('id', 'id'),
            ('name', 'name'),
            ('link', 'link'),
        )
    
        for data_field, registration_field in mapping:
            if data_field in data:
                results[registration_field] = data[data_field]

        # Return results
        return results

    #Not yet implemented
    def get_registration_dict(self, access_token):
        return self.get_registration_fields(access_token)

    def add_foursquare_user_record(self, access_token, user):
        client = self.make_foursquare_client()
        client.set_access_token(access_token)
        print client.users()['user']['firstName']
        
        try:
            foursquare_user = UserFoursquare.objects.get(user=user)
            return None
        except UserFoursquare.DoesNotExist:
            record = UserFoursquare()
            record.user = user
            record.oauth_access_token = access_token
            client = self.make_foursquare_client()
            client.set_access_token(access_token)
            data = client.users()

    #Not yet implemented
    def get_facebook_user_id(self, access_token):
        data = self.get_facebook_user_fields(access_token)
        if 'id' in data:
            return data['id']
        else:
            return None

    #Not yet implemented
    def get_user_by_facebook_user_id(self, access_token):
        facebook_user_id = self.get_facebook_user_id(access_token)
        if facebook_user_id is not None:
            try:
                facebook_user = UserFacebook.objects.get(
                    facebook_graphid = facebook_user_id
                )
                return facebook_user.user
            except UserFacebook.DoesNotExist:
                pass
        return None
