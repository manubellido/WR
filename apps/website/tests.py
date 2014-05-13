# -*- coding: utf-8 -*-

from django.utils import unittest
from django.test.client import Client
from django.core.urlresolvers import reverse


class WebsiteTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_work_urls(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('recommended_circuits'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('privacy_policy'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('terms_of_use'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('who_we_are'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('about_worldrat'))
        self.assertEqual(response.status_code, 200)
