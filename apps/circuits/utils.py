# -*- coding: utf-8 -*-

"""
Utils in the "circuits" app
"""

from ordereddict import OrderedDict
from django.conf import settings
from django.core.urlresolvers import reverse
from rest.utils import render_as_json
from circuits.constants import CIRCUIT_CATEGORY_CHOICES


class CircuitCategory(object):

    def __init__(self, category_id):
        try:
            category_id = int(category_id)
        except ValueError:
            category_id = CIRCUIT_CATEGORY_CHOICES.get_value(category_id)
        self._id = category_id

    @property
    def id(self):
        return self._id

    @property
    def key(self):
        return CIRCUIT_CATEGORY_CHOICES.get_key(self._id)

    @property
    def name(self):
        return CIRCUIT_CATEGORY_CHOICES.get_string(self._id)

    # Deprecated use name property instead
    @property
    def description(self):
        return CIRCUIT_CATEGORY_CHOICES.get_string(self._id)

    @property
    def slug(self):
        if hasattr(self, "key") and self.key:
            return u'%s' % (self.key.lower())
        else:
            return u''

    def __unicode__(self):
        return u'%s' % self.description

    def __repr__(self):
        return u'<CircuitCategory #%d: "%s">' % (self.id, self.description)

    def get_absolute_url(self):
        return reverse('circuit_category_listing',
                       kwargs={'category_slug': self.slug})

    def get_restful_url(self):
        return "%s%s" % (
            settings.API_V1_PREFIX.rstrip('/'),
            reverse(
                'circuit_category_resource',
                kwargs={'category_slug': self.slug}
            )
        )

    def get_json_representation(self, render_json=True):
        document = OrderedDict()
        document['id'] = self.id
        document['slug'] = self.slug
        document['description'] = unicode(self.description)
        document['link'] = self.get_restful_link_metadata('self')
        if render_json:
            return render_as_json(document)
        else:
            return document

    def get_restful_link_metadata(self, rel='alternate'):
        metadata = OrderedDict()
        metadata['href'] = self.get_restful_url()
        metadata['rel'] = rel
        metadata['title'] = unicode(self.description)
        metadata['type'] = 'application/json'
        metadata['id'] = self.id #FIXME Delete this line
        return metadata

    def is_followed(self, user):
        return hasattr(user, 'categories') and \
            user.categories.filter(category=self.id).exists()

    def get_value(self):
        return int(self._id)


def circuit_category_list():
    results = []
    for record in CIRCUIT_CATEGORY_CHOICES:
        category_id = record[0]
        results.append(CircuitCategory(category_id))
    return results


def circuit_category_dict():
    result = OrderedDict()
    for record in CIRCUIT_CATEGORY_CHOICES:
        category_id = record[0]
        result[category_id] = CircuitCategory(category_id)
    return result
