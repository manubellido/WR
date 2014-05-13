# -*- coding: utf-8 -*-

from django import forms
from googlemaps_localities import strings, constants

class LatLngValidationForm(forms.Form):

    lat = forms.FloatField(
        required=False
    )
    
    lng = forms.FloatField(
        required=False
    )

    def clean_lat(self):
        lat = self.cleaned_data.get('lat', None)
        if lat is not None and \
            (lat < constants.LATITUDE_MIN_VALUE or \
            lat > constants.LATITUDE_MAX_VALUE):
            raise forms.ValidationError(
                strings.WRONG_LATITUDE_VALUE
            )
        return lat

    def clean_lng(self):
        lng = self.cleaned_data.get('lng', None)
        if lng is not None and \
            (lng < constants.LONGITUDE_MIN_VALUE or \
            lng > constants.LONGITUDE_MAX_VALUE):
            raise forms.ValidationError(
                strings.WRONG_LONGITUDE_VALUE
            )
        return lng

    def clean(self):
        if len(self.errors) == 0:

            lat = self.cleaned_data.get('lat', None)
            lng = self.cleaned_data.get('lng', None)

            if lat is None or lng is None:
                raise forms.ValidationError(
                    strings.MISSING_COORDINATES_INFORMATION
                )

        return self.cleaned_data

