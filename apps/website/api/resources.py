# -*- coding: utf-8 -*-

from haystack.query import SearchQuerySet
from ordereddict import OrderedDict
from django.http import HttpResponse
from django.conf import settings
from rest.views import FunctionResourceView
from rest.utils import render_as_json
from django.template.loader import render_to_string


RESULTS_PER_PAGE = getattr(settings, 'HAYSTACK_SEARCH_RESULTS_PER_PAGE', 10)

class SearchMoreFunction(FunctionResourceView):
    """
    REST API returns the results from search
    """
    def post(self,request, *args, **kwargs):
        term = request.POST.get('category_type','')
        page = request.POST.get('page',1)
        next_page = int(page) + 1
        start = (RESULTS_PER_PAGE*int(page))
        end = (RESULTS_PER_PAGE*next_page)
        search = (
                SearchQuerySet().filter(content=term)|
                SearchQuerySet().filter(placetitle=term)|
                SearchQuerySet().filter(placedescription=term)|
                SearchQuerySet().filter(placeaddress=term)
                )[start:end]
        document = OrderedDict()
        document['page'] = next_page

        if not search:
            document['hide_button'] = True

        else:
            raw_html = u''
            for element in search:
                raw_html += render_to_string(
                        'circuits/circuit_list_item.html',
                        {'circuit': element.object, 'user': request.user}
                )
            document['count'] =  len(search)
            document["raw_html"] = raw_html

        return HttpResponse(
            content=render_as_json(document),
            content_type='application/json'
        )
