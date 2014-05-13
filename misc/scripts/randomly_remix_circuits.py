"""
Script to randomly remix circuits
Coded by Javier Olaechea <javier@worldrat.com>
"""

import random
from circuits.models import Circuit
from user_profile.models import UserProfile

circuits = Circuit.objects.all()
profiles = UserProfile.objects.all()
countdown = 100

while countdown > 0:
    circuit = random.choice( circuits )
    profile = random.choice( users )
    circuit.remix(profile.user)
    countdown -= 1
