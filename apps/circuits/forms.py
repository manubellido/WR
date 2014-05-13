# -*- coding: utf-8 -*-

import re
from ordereddict import OrderedDict

from django import forms

from common.forms.widgets import SelectWithEmptyLabelForEnumerations
from common.utils.strings import multiple_whitespace_to_single_space
from topics.models import Topic
from circuits.models import Circuit, CircuitStop
from circuits.validators import validate_not_zero
from circuits import constants, strings


class CircuitForm(forms.Form):

    name = forms.CharField(
        max_length=256,
        widget=forms.TextInput(attrs={
            'class': 'route-name'})
    )

    category = forms.ChoiceField(
        choices=constants.CIRCUIT_CATEGORY_CHOICES,
        validators=[validate_not_zero],
        widget=SelectWithEmptyLabelForEnumerations(
            choices=constants.CIRCUIT_CATEGORY_CHOICES,
            empty_label=strings.CHOOSE_CATEGORY
        )
    )

    topics = forms.CharField(
        max_length=512,
        required=False
    )

    description = forms.CharField(
        max_length=512,
        widget=forms.Textarea(attrs={'rows': '', 'cols': '', 'maxlength': '512'}),
        required=False,
    )

    adult_content = forms.BooleanField(
        required=False
    )

    class Meta:
        model = Circuit
        fields = ('name', 'category', 'adult_content')


    def clean_name(self):
        name = self.cleaned_data['name']
        name = multiple_whitespace_to_single_space(name).strip()
        return name

    def clean_topics(self):
        topics = self.cleaned_data['topics'].strip()
        if topics:
            topics = ', '.join(Topic.parse_names(topics))
        return topics

    def process_objects(self, author):
        name = self.cleaned_data.get('name', u'')
        category = self.cleaned_data.get('category',
            constants.DEFAULT_CIRCUIT_CATEGORY)
        description = self.cleaned_data.get('description', u'')

        # Trimming more than one 2 linebreaks to one
        line_breaks = re.search('.*?(\s{2,}).*?', description)
        if line_breaks is not None:
            trimmed_description = description
            for line_break in line_breaks.groups():
                trimmed_description = description.replace(line_break, u'\r\n')
            description = trimmed_description

        # Circuit
        circuit = Circuit(
            name=name,
            category=category,
            description=description,
            author=author,
            adult_content=self.cleaned_data.get('adult_content', False)
        )
        circuit.save()

        # Topics
        new_topics = []
        all_topics = []
        topic_names = Topic.parse_names(self.cleaned_data.get('topics', []))
        for tn in topic_names:
            if not Topic.exists(tn):
                topic = Topic.get_or_create(tn)
                new_topics.append(topic)
            else:
                topic = Topic.get_by_name(tn)
            all_topics.append(topic)

        multiple = False
        if len(new_topics) > 0:
            multiple = True

        # Add topics to circuit
        for topic in all_topics:
            circuit.topics.add(topic)

        circuit.save()

        return {
            'circuit': circuit,
            'all_topics': all_topics,
            'new_topics': new_topics,
            'multiple': multiple
        }


def make_categories_form():
    categories = constants.CIRCUIT_CATEGORY_CHOICES
    fields = OrderedDict()
    for value in categories.values():
        fields[str(value)] = forms.BooleanField(
                required=False,
                label=categories.get_string(value),
                widget=forms.CheckboxInput(attrs={'value': value}),
                help_text=u'cat-%s' % (value, ),  # Hack, used for css
            )

    return type('CategoriesForm',
                (forms.BaseForm,),
                {'base_fields': fields}
            )


class StopEditForm(forms.ModelForm):

    class Meta:
        model = CircuitStop
        widgets = {
                'description': forms.Textarea(attrs={
                    'maxlength': '512',
                    'cols': '',
                    'rows': '',
                    }),
                }
        fields = ('description', 'picture',)
