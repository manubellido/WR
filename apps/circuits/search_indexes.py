# -*- coding: utf-8 -*-

from haystack import indexes
from circuits.models import Circuit

class CircuitIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author')
    author_username = indexes.CharField(model_attr='author__username')
    name = indexes.CharField(model_attr='name')
    published = indexes.BooleanField(model_attr='published')
    description = indexes.CharField(model_attr='description',null=True)
    placedescription = indexes.MultiValueField(indexed=True)
    placetitle = indexes.MultiValueField(indexed=True)
    placeaddress = indexes.MultiValueField(indexed=True)

    def prepare_placedescription(self,obj):
        return [c.description for c in obj.circuit_stops.all()]

    def prepare_placetitle(self,obj):
        return [c.place.name for c in obj.circuit_stops.all()]

    def prepare_placeaddress(self,obj):
        return [c.place.address for c in obj.circuit_stops.all()]

    def get_model(self):
        return Circuit

    def get_description(self, obj):
        if obj is None:
            return ''

    def prepare_author(self, obj):
        obj.author.get_full_name()
