# -*- coding: utf-8 -*-

import random
from django.contrib.gis.db import models
from django.db import models as basic_models
from common.models import AuditableModel
from django.contrib.auth.models import User
from common.datastructures import Enumeration
from circuits import constants
    

class SimUser(AuditableModel):
    """
    Basic User with some extra fields
    """

    GENDER_CHOICES = (
        (1, 'MALE'),
        (2, 'FEMALE'),
        (3, 'UNDISCLOSED')
    )

    gender = models.PositiveIntegerField(choices=GENDER_CHOICES)

    user = models.OneToOneField(User)

    free_time_score = models.IntegerField(null=True)
    explorer_score = models.IntegerField(null=True)
    pop_score = models.IntegerField(null=True)
    circuits_to_create = models.IntegerField(null=True)

    def __unicode__(self):
        return self.user.username

    def set_gender(self):
        """
        Assuming female = 51%, male=47%, undisclosed=2%
        """
        chance = random.randint(0,100)

        if chance <= 51:
            gender = 2
        elif chance > 51 and chance <= 98:
            gender = 1
        else:
            gender = 3

        self.gender = gender
        self.save()

class SimulationInfo(basic_models.Model):
    """
    Model contaning information on a day simulation
    """

    date = basic_models.DateTimeField()
    num_users_created = basic_models.IntegerField(null=True)
    num_circuits_created = basic_models.IntegerField(null=True)
    num_visits_created = basic_models.IntegerField(null=True)
    num_follows_created = basic_models.IntegerField(null=True)

    # TODO: Fix this functionallity
#    def Get_last_date(self):
#        """
#        Returns the last simulated date on the DB
#        """
#        big_id = -1
#        all_dates = session.query(Simulation_info)
#        for fecha in all_dates:
#            if fecha.id > big_id:
#                big_id = fecha.id
#                last_date = fecha.date
#
#        return last_date
