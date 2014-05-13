# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from circuits.models import Circuit
from django.core.urlresolvers import reverse
from django.conf import settings
class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        circuits = Circuit.objects.all()
        for circuit in circuits:
            sufix =reverse('circuit_detail_with_slug', 
                kwargs={
                    'circuit_id': circuit.id,
                    'slug': circuit.slug
                })
            prefix = settings.SITE_PREFIX
            print '%s%s' % (prefix,sufix)
