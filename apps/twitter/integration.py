# -*- coding: utf-8 -*-

import re
import requests
import simplejson

import tweepy
from django.core.urlresolvers import reverse
from django.conf import settings

from user_profile.integration import GenericIntegrator
from user_profile.models import UserTwitter
from django_countries.countries import COUNTRIES


class TwitterIntegrator(GenericIntegrator):

    def get_oauth_client_id(self):
        return settings.TWITTER_CONSUMER_KEY

    def get_oauth_secret(self):
        return settings.TWITTER_CONSUMER_SECRET

    def get_full_login_end_url(self):
        return ''.join([
            settings.SITE_PREFIX,
            reverse('twitter_login_redirection_end')
        ])

    def get_full_registration_end_url(self):
        return ''.join([
            settings.REDIRECTOR_PREFIX,
            '/twitter'
            #reverse('twitter_registration_redirection_end')
        ])

    def create_twitter_auth(self, redirect_uri=None):
        args = []
        args.append(self.get_oauth_client_id())
        args.append(self.get_oauth_secret())
        if redirect_uri:
            args.append(redirect_uri)
        auth = tweepy.OAuthHandler(*args)
        return auth

    def create_authorization_url(self, redirect_uri):
        auth = self.create_twitter_auth(redirect_uri)
        result = auth.get_authorization_url()
        print 'balls'
        print result
        self.request_token = auth.request_token
        return result
        #FIXME: Add proper exception handling and notification to the 
        #end user when this routine fails from the Twitter end
        #except tweepy.TweepError:
        #    return None

    def get_request_token_key(self):
        request_token = getattr(self, 'request_token', None)
        if request_token is not None:
            return request_token.key
        else:
            return None

    def get_request_token_secret(self):
        request_token = getattr(self, 'request_token', None)
        if request_token is not None:
            return request_token.secret
        else:
            return None

    def get_user_information_as_json(self,
                                     acc_token_key,
                                     acc_token_secret,
                                     picture_size):
        result = {}
        auth = self.create_twitter_auth()
        auth.set_access_token(acc_token_key, acc_token_secret)
        api = tweepy.API(auth)
        me = api.me()
        fields = (
            'name',
            'screen_name',
            'description',
            'url',
            'location',
            'profile_image_url',
        )
        for f in fields:
            result[f] = getattr(me, f, None)
        # Manually add id as string
        result['id'] = str(me.id)
        # Add image size
        suffix = '_' + picture_size
        if picture_size == 'original':
            suffix = ''

        result['profile_image_url'] = result['profile_image_url'].replace('_normal', suffix)
        return result

    def get_user_picture(self, acc_token_key, acc_token_secret, picture_size):
        data = self.get_user_information_as_json(
            acc_token_key,
            acc_token_secret,
            picture_size
        )
        return data.get('profile_image_url', None)

    def get_registration_fields(self, acc_token_key, acc_token_secret):
        results = {}

        data = self.get_user_information_as_json(
            acc_token_key, 
            acc_token_secret
        )

        # Direct mappings
        mapping = (
            ('screen_name', 'username'),
        )
        for data_field, registration_field in mapping:
            if data_field in data:
                results[registration_field] = data[data_field]

        # Manual mappings

        # Name
        if 'name' in data:
            name = data['name']
            name_parts = name.split(', ')
            if len(name_parts) > 0:
                data['fist_name'] = name_parts[0]
            if len(name_parts) > 1:
                data['last_name'] = name_parts[1]

        # Country
        if 'location' in data:
            location_name = data['location']
            location_parts = location_name.split(', ')
            if location_parts > 0:
                possible_country_name = location_parts[-1]
            for country_code, country_name in COUNTRIES:
                if possible_country_name.lower() == country_name.lower():
                    results['country'] = country_code

        # Return result dictionary
        return results

    def get_account_extra_fields(self, acc_token_key, acc_token_secret):
        results = {}
        data = self.get_user_information_as_json(
            acc_token_key,
            acc_token_secret
        )

        # Direct mappings
        mapping = (
            ('description', 'bio'),
            ('url', 'website'),
            ('profile_image_url', 'picture'), 
        )

        for data_field, registration_field in mapping:
            if data_field in data:
                results[registration_field] = data[data_field]

        # Manual mappings

        # Return results
        return results

    def get_twitter_user_fields(self, acc_token_key, acc_token_secret):
        results = {}
        data = self.get_user_information_as_json(
            acc_token_key,
            acc_token_secret
        )

        # Direct mappings
        mapping = (
            ('id', 'id'),
            ('name', 'name'),
            ('screen_name', 'screen_name'),
        )

        for data_field, registration_field in mapping:
            if data_field in data:
                results[registration_field] = data[data_field]

        # Return results
        return results

    def get_registration_dict(self, acc_token_key, acc_token_secret):
        return self.get_registration_fields(
            acc_token_key,
            acc_token_secret
        )

    def add_twitter_user_record(self, acc_token_key, acc_token_secret, user):
        try:
            twitter_user = UserTwitter.objects.get(user=user)
            return None
        except UserTwitter.DoesNotExist:
            record = UserTwitter()
            record.user = user
            record.oauth_token_key = acc_token_key
            record.oauth_token_secret = acc_token_secret
            data = self.get_twitter_user_fields(
                acc_token_key, 
                acc_token_secret
            )
            record.twitter_user_id = data['id']
            record.name = data['name']
            record.link = data['screen_name']
            record.save()
            return record

    def get_twitter_user_id(self, acc_token_key, acc_token_secret):
        data = self.get_twitter_user_fields(acc_token_key, acc_token_secret)
        if 'id' in data:
            return data['id']
        else:
            return None

    def get_user_by_twitter_user_id(self, acc_token_key, acc_token_secret):
        twitter_user_id = self.get_twitter_user_id(
            access_token_key,
            access_token_secret
        )
        if twitter_user_id is not None:
            try:
                twitter_user = TwitterUser.objects.get(
                    twitter_user_id = twitter_user_id
                )
                return twitter_user.user
            except TwitterUser.DoesNotExist:
                pass
        return None

    def get_access_token_dict(self, redirect_uri, rtk, rts, verifier):
        access_token_dict = {}
        auth = self.create_twitter_auth(redirect_uri)
        auth.set_request_token(rtk, rts)
        try:
            access_token_dict['key'] = auth.access_token.key
            access_token_dict['secret'] = auth.access_token.secret
            return access_token_dict
        except tweepy.TweepError, e:
            return None
