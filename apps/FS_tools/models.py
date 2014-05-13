# -*- coding: utf-8 -*-
from django.contrib.gis.db import models
try:
    import json
except ImportError:
    import simplejson as json
    
from django.conf import settings
from places.models import Place
from circuits.models import CircuitStop
from FS_tools import strings


class FSPhoto(models.Model):
    """
    Replicates the photo model of 4SQR and is intended to be plugged
    to diferent models like CircuitStop
    """
    
    # PK field, just like in Foursquare
    photo_id = models.CharField(
        primary_key=True,
        max_length=32,
    )
    
    url = models.CharField(
        verbose_name=strings.FSPHOTO_URL,
        max_length=256,
    )
    
    width = models.IntegerField(
        verbose_name=strings.FSPHOTO_WIDTH,
        blank=True,
        null=True,
    )
    
    height = models.IntegerField(
        verbose_name=strings.FSPHOTO_HEIGHT,
        blank=True,
        null=True,
    )
    
    # 4SQR user_id just in case
    user_id = models.CharField(
        verbose_name=strings.FSPHOTO_USERID,
        max_length=32,
        blank=True,
        null=True,
    )
    
    def __unicode__(self):
        return u'%s' % (self.photo_id,)

    class Meta:
        verbose_name = strings.FSPHOTO_VERBOSE_NAME
        verbose_name_plural = strings.FSPHOTO_VERBOSE_NAME_PLURAL
        
    
class CircuitStopFSAdapter(models.Model):
    """
    Model relating many photos to a CircuitStop and methods for manipulating
    these photos and 4SQR
    """
    
    # Relation with CircuitStop
    circuitstops = models.OneToOneField(
        CircuitStop,
        related_name='foursquare',
    )
    
    # Relation with many FSPhotos
    photos = models.ManyToManyField(
        FSPhoto,
        blank=True,
        null=True,
    )
    
    def __unicode__(self):
        return u'Adapter of CircuitStop %s' % (self.circuitstops.circuit.name,)

    class Meta:
        verbose_name = strings.STOPADAPTER_VERBOSE_NAME
        verbose_name_plural = strings.STOPADAPTER_VERBOSE_NAME_PLURAL
        
    def get_number_photos(self):
        """
        returns the number of photos associated with self.circuitstops
        """
        return self.photos.objects.all().count()
        
    
    def load_from_FS(self, limit=1, group='venues'):
        """
        returns a list of FS photos assigned to current 
        circuitstops.place.place_id, group can also be 'checkins' or 'tips'
        limit = number of photos to return
        """
        pass
    
    
        
        
