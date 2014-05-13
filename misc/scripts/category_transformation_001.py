# -*- coding: utf-8 -*-

from circuits.models import Circuit
from circuits.utils import CircuitCategory

"""
Transformaciones
Literary + Culture + Music + Art + Academic & Education =>  Arts & Culture
3          4         8        10    19                   =>  4
Lifestyle + Green + Fashion + Design + Technology + Business + Geek + Spiritual + Entertainment => Lifestyle
18          7       6         11       16           14         17     21          25               18
"""

for circuit in Circuits.objects.filter(category__in=[3, 8, 10, 19]):
    circuit.category = 4
    circuit.save()

for circuit in Circuits.objects.filter(category__in=[7, 6, 11, 16, 14, 17, 21, 25]):
    circuit.category = 18
    circuit.save()
