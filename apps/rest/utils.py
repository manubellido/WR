# -*- coding: utf-8 -*-

from ordereddict import OrderedDict
from rest.serializers import RESTfulJSONEncoder


def render_as_json(document, indent=4):
    if type(indent) == int:
        indent = ' ' * indent
    encoder = RESTfulJSONEncoder(indent=indent)
    return encoder.encode(document)

def error_document(error_list=[]):
    document = OrderedDict()
    if len(error_list) == 1:
        document['error'] = error_list[0]
    elif len(error_list) >= 2:
        document['errors'] = error_list
    return document

def json_error_document(error_list=[], indent=4):
    document = error_document(error_list)
    return render_as_json(document, indent)

def error_list_from_form(form, prefix_with_fields=True):
    results = []
    errors = OrderedDict(form.errors)
    for field, messages in errors.iteritems():
        for message in messages:
            entry = OrderedDict()
            if prefix_with_fields and field != '__all__':
                message = '%s: %s' % (field, message)
            entry['message'] = unicode(message)
            results.append(entry)
    return results
