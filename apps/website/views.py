# -*- coding: utf-8 -*-

import simplejson as json
from simplejson.decoder import JSONDecodeError
from ordereddict import OrderedDict

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import (HttpResponse,
    HttpResponseBadRequest, 
    HttpResponseRedirect
)

from rest.utils import render_as_json

from django.shortcuts import render_to_response
from django.template import RequestContext
from circuits.models import Circuit
from circuits.utils import circuit_category_list
import circuits.settings as circuit_settings

from googlemaps_localities.models import GoogleMapsAddressComponent as GMAC
from googlemaps_localities.decorators import set_gmac

from website.utils import validate_section
from website.utils import create_title
from website.utils import create_url
from website import strings


RESULTS_PER_PAGE = getattr(settings, 'HAYSTACK_SEARCH_RESULTS_PER_PAGE', 10)

def haystack_search(request):
    from haystack.query import SearchQuerySet
    from haystack.forms import ModelSearchForm
    from django.core.paginator import Paginator

    template = 'search/search.html'
    results_per_page = RESULTS_PER_PAGE
    form_class = ModelSearchForm
    term = request.GET.get('q','')
    page = 0
    next_page = int(page) + 1
    start = (results_per_page * int(page) )
    end = (results_per_page * next_page) + 1 #Minor hack to speed up results

    data = request.GET
    form = form_class(data)

    search = (
        SearchQuerySet().filter(content=term).exclude(published=False)|
        SearchQuerySet().filter(placetitle=term).exclude(published=False)|
        SearchQuerySet().filter(placedescription=term).exclude(published=False)|
        SearchQuerySet().filter(placeaddress=term).exclude(published=False)
    )

    search = search[start:end]

    paginator = Paginator(search, results_per_page)
    page = paginator.page(1)

    context = {
        'query': term,
        'form': form,
        'page': page,
        'paginator': None,
        'suggestion': None,
    }
    return render_to_response(template, context,
        context_instance=RequestContext(request)
    )

@set_gmac
def show_home(request, gmac_slug=None):

    # Find GMAC
    gmacs = None
    if gmac_slug is not None:
        try:
            gmacs = GMAC.objects.filter(slug=gmac_slug)
        except GMAC.DoesNotExist:
            pass

    params = {}

    gmac_get_short_formatted_name = None
    if gmacs is not None:
        params['pk__in'] = [c.pk for c in Circuit.filter_by_gmacs(gmacs)]
        gmac_get_short_formatted_name = gmacs[0].get_short_formatted_name()

    cpp = circuit_settings.DEFAULT_CIRCUITS_LIMIT

    if request.is_ajax():
        page = request.POST.get('page', None)
        if page is not None:
            page = int(page)
        else:
            error_doc = OrderedDict()
            error_doc['error'] = unicode(strings.MISSING_PAGE_PARAM_ERROR)
            return HttpResponse(
                content=render_as_json(error_doc),
                content_type='application/json'
            )

        response = {
            'page': int(page) + 1
        }

        circuits = Circuit.objects.filter(**params)
        circuits = circuits.filter(published=True).order_by(
            '-highlighted', '-modified'
        )[page * cpp: cpp * (page + 1)]

        if circuits:
            html_response = u''

            for circuit in circuits:
                html_response += render_to_string(
                    'circuits/circuit_list_item.html',
                    {'circuit': circuit, 'user': request.user})
            response['raw_html'] = html_response
        else:
            response['hide_button'] = True

        return HttpResponse(
            json.dumps(response),
            mimetype='application/json'
        )

    categories = circuit_category_list()

    # Circuits that are not flagged as 18+
    circuits = Circuit.objects.filter(adult_content=False)
    circuits = circuits.filter(published=True).order_by('?')[:cpp]

    return render(request,
        'circuits/recommendations.html',
        {
            'categories': categories,
            'circuits': circuits,
            'topbar_item': 'explore',
            'page_type': 'recommendation',
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
            'gmac_slug': gmac_slug,
            'gmacs': gmacs,
            'gmac_get_short_formatted_name': gmac_get_short_formatted_name,
        },
    )

def change_lang(request, lang_id):
    """ Changes the language on the current session if user is
        anonymous or sets the UserProfile language preference 
        if authenticated lang_id: 1=ENGLISH, 2=ESPANIOL"""
        
    from user_profile.constants import LANGUAGE_CHOICES
    # get posible languages ids from constants
    posible_languages_ids = LANGUAGE_CHOICES.values()
    # change type to int in order to compare and store in DB
    lang_id = int(lang_id)

    # check if lang_id is within possibilities
    if lang_id in posible_languages_ids:
        # user exists
        if hasattr(request, 'user'):
            if request.user.is_authenticated():
                up = request.user.userprofile
                up.language = lang_id
                up.save()

        request.session['django_language'] = \
            settings.LANGUAGES[lang_id - 1][0]
        # Build response
        response = HttpResponseRedirect(
            request.META['HTTP_REFERER'],
        )
        # set a cookie and response
        response.set_cookie(
            'django_language', 
            settings.LANGUAGES[lang_id - 1][0]
        )
        return response

    # return to the previous URL
    return HttpResponseRedirect(
        request.META['HTTP_REFERER'],
    )


@set_gmac
def test_recsys(request, gmac_slug=None):
    """
    Testing recsys view
    """
    from recsys.circuits.circuit_recsys import CircuitRecsys

    # Find GMAC
    gmacs = None
    gmac_id = None
    gmac_get_short_formatted_name = None
    filtered_circuits = None
    if gmac_slug is not None:
        try:
            gmacs = GMAC.objects.filter(slug=gmac_slug)
            filtered_circuits = Circuit.filter_by_gmacs(gmacs)
            gmac_get_short_formatted_name = gmacs[0].get_short_formatted_name()
            gmac_id = gmacs[0].pk
        except GMAC.DoesNotExist:
            pass
        except IndexError:
            pass
    
    categories = circuit_category_list()

    circuits = Circuit.objects.filter(**params)
    circuits = circuits.filter(published=True)
    circuits = circuits.select_related(depth=3).order_by(
        '-highlighted', '-modified'
    )[:cpp]

    return render(request,
        'circuits/recommendations.html',
        {
            'categories': categories,
            'circuits': circuits,
            'topbar_item': 'explore',
            'page_type': 'recommendation',
            'STATIC_MAPS_ROOT': settings.STATIC_MAPS_ROOT,
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
            'gmac_slug': gmac_slug,
            'gmacs': gmacs,
            'gmac_get_short_formatted_name': gmac_get_short_formatted_name,
        },
    )

@set_gmac
def test_recsys(request, gmac_slug=None):
    """
    Testing recsys view
    """
    from recsys.circuits.circuit_recsys import CircuitRecsys

    # Find GMAC
    gmacs = None
    gmac_id = None
    gmac_get_short_formatted_name = None
    filtered_circuits = None
    if gmac_slug is not None:
        try:
            gmacs = GMAC.objects.filter(slug=gmac_slug)
            filtered_circuits = Circuit.filter_by_gmacs(gmacs)
            gmac_get_short_formatted_name = gmacs[0].get_short_formatted_name()
            gmac_id = gmacs[0].pk
        except GMAC.DoesNotExist:
            pass
        except IndexError:
            pass
    
    categories = circuit_category_list()

    if request.user.is_authenticated():
        # Recsys functionallity
        recsys = CircuitRecsys(request.user.pk)
        if gmac_id is None:
            gmac_id = request.session.get('gmac_id', None)
        if gmac_id is not None:
            recsys.Set_gmac(gmac_id)
        circuits_ids = recsys.Give_me_the_fun(top_n=15)
        circuits = Circuit.objects.filter(id__in=circuits_ids).\
            filter(published=True)

        if filtered_circuits is not None : 
            circuits = [val for val in filtered_circuits if val in circuits]

    else:
        if gmac_id is not None:
            gmac = GMAC.objects.get(pk=gmac_id)
            circuits = Circuit.filter_by_gmac(gmac)
        else:
            # case when gmac is not detected
            cpp = circuit_settings.DEFAULT_CIRCUITS_LIMIT
            circuits=Circuit.objects.all()[:cpp]

    return render(request,
        'circuits/recommendations.html',
        {
            'categories': categories,
            'circuits': circuits,
            'topbar_item': 'explore',
            'page_type': 'recommendation',
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
            'gmac_slug': gmac_slug,
            'gmacs': gmacs,
            'gmac_get_short_formatted_name': gmac_get_short_formatted_name,
        },
    )

def change_location(request):

    if request.method == 'POST':
        message = unicode(strings.CHANGE_LOCATION_DOCUMENT_ERROR)
        try:
            # Parse data
            data = json.loads(request.body)
            section = data.get('section', None)
            components = data.get('address_components', None)

            section_ok = validate_section(section)
            aux_doc = OrderedDict()
            aux_doc['results'] = [{
                'address_components': components
            }]
            json_string = json.dumps(aux_doc)

            # Grab an address component
            gmac = GMAC.get_or_create_locality_from_json(json_string)

            if section_ok and gmac is not None:
                title = create_title(gmac, section)
                url = create_url(gmac, section)
                # Make response document
                doc = OrderedDict()
                doc['link'] = OrderedDict()
                doc['link']['title'] = title
                doc['link']['href'] = url
                doc['link']['rel'] = 'section'
                return HttpResponse(
                    content=render_as_json(doc),
                    content_type='application/json'
                )
            elif not section_ok:
                message = unicode(strings.SECTION_IS_INVALID)
            elif gmac is None:
                message = unicode(strings.GMAC_NOT_FOUND)
        except JSONDecodeError:
            pass

        # At this point the request is somewhat borked
        doc = OrderedDict()
        doc['errors'] = [message]
        return HttpResponseBadRequest(
            content=render_as_json(doc),
            content_type='application/json'
        )
    else:
        message = unicode(strings.CHANGE_LOCATION_ERROR)
        doc = OrderedDict()
        doc['errors'] = [message]
        return HttpResponseBadRequest(
            content=render_as_json(doc),
            content_type='application/json'
        )

def  privacy_policy(request):
    return render(request,
            'website/privacy_policy.html',
            {},
        )


def terms_of_use(request):
    return render(request,
            'website/terms_of_use.html',
            {},
        )


def who_we_are(request):
    return render(request,
            'website/who_we_are.html',
            {},
        )


def about_worldrat(request):
    return render(request,
            'website/about_worldrat.html',
            {},
        )
