# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.forms.fields import FileField


class PatchModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        for fieldname in self.base_fields:
            self.base_fields[fieldname].required = False
        self.empty_permited = True
        return super(PatchModelForm, self).__init__(*args, **kwargs)

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            value = field.widget.value_from_datadict(
                self.data,
                self.files,
                self.add_prefix(name)
            )
            # this is the key difference with the inherited behavior so fields
            # not present in the bound data do not get updated with None values
            if self.add_prefix(name) not in self.data:
                continue
            try:
                if isinstance(field, FileField):
                    initial = self.initial.get(name, field.initial)
                    value = field.clean(value, initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except ValidationError, e:
                self._errors[name] = self.error_class(e.messages)
                if name in self.cleaned_data:
                    del self.cleaned_data[name]
