# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from circuits.models import Circuit

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        
        Circuit.objects.all().order_by('?')[:8]
