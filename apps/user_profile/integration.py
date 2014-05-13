# -*- coding:utf-8 -*-

import simplejson
import requests
from django.core.urlresolvers import reverse


class GenericIntegrator(object):

    def get_registration_dict(self, *args, **kwargs):
        return {}

    def get_registration_form_url(self):
        return reverse('registration_form')


class OAuthIntegrator(GenericIntegrator):

    def get_oauth_client_id(self):
        return ''

    def get_oauth_secret(self):
        return ''

    def get_oauth_permissions(self):
        return []

    def get_oauth_scope(self):
        return ','.join(self.get_oauth_permissions())

    def get_base_authorization_url(self):
        return ''

    def get_base_access_token_retrieval_url(self):
        return ''

    def create_authorization_url(self, redirect_uri):
        return '%s?client_id=%s&redirect_uri=%s&scope=%s' % (
            self.get_base_authorization_url(),
            self.get_oauth_client_id(),
            redirect_uri,
            self.get_oauth_scope()
        )

    def create_login_url(self, redirect_uri):
        return '%s?client_id=%s&redirect_uri=%s' % (
            self.get_base_authorization_url(),
            self.get_oauth_client_id(),
            redirect_uri
        )

    def create_access_token_retrieval_url(self, redirect_uri, code):
        return '%s?client_id=%s&redirect_uri=%s&client_secret=%s&code=%s' % (
            self.get_base_access_token_retrieval_url(),
            self.get_oauth_client_id(),
            redirect_uri,
            self.get_oauth_secret(),
            code
        )

    def get_access_token(self, redirect_uri, code):
        data = {}
        url = self.create_access_token_retrieval_url(redirect_uri, code)
        #print url
        response = requests.get(url)
        try:
            json_response = simplejson.loads(response.content)
            return None
        except simplejson.JSONDecodeError:
            #print response.content
            parts = response.content.split('|')
            for p in parts:
                sections = p.split('&')  #TODO: Improve
                for s in sections:
                    k, v = s.split('=')
                    data[k] = v
            if 'access_token' in data:
                return data['access_token']
            else:
                return None
