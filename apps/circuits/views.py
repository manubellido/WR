# -*- coding: utf-8 -*-

import json
from ordereddict import OrderedDict

from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string, get_template
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden, Http404, HttpResponseBadRequest)
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.conf import settings
from django.shortcuts import redirect

from rest.utils import render_as_json
from circuits import strings
from circuits.api.forms import (CircuitStopCreationControllerForm,
                                CircuitPictureControllerForm,
                                CircuitUpdateControllerForm)
from circuits.constants import CIRCUIT_CATEGORY_CHOICES, EMBEDDING_FAIL_VALUES
from circuits.forms import CircuitForm, StopEditForm, make_categories_form
from circuits.models import (Circuit, CircuitStop, CircuitCategoryFollow,
                             CircuitRelatedUserProxy)
from circuits.utils import CircuitCategory, circuit_category_list
from circuits import settings as circuit_settings
from circuits.signals import circuit_visited
from googlemaps_localities.models import GoogleMapsAddressComponent as GMAC
from places.models import PlaceType
from rest.utils import (error_list_from_form, json_error_document)
from notifications.models import NotifiableEvent
from user_profile.signals import category_follow, category_unfollow



@require_POST
@login_required
def remix_circuit(request, circuit_id):
    """
    View for remixing a circuit, takes care of cloning the circuit and
    stops and redirects to the edit_circuit view of the new created circuit
    TODO: Make Circuit not salvable.
    """
    new_title = request.POST.get('name')
    new_category = request.POST.get('category')
    new_description = request.POST.get('description')
    new_adult_content = request.POST.get('adult_content')

    # try to get the circuit from DB
    circuit = get_object_or_404(Circuit,
        pk=circuit_id,
    )

    # call circuits remix method
    remixed_circuit = circuit.remix(
            new_author=request.user,
            new_title=new_title,
            new_category=new_category,
            new_description=new_description,
            adult_content=new_adult_content,
        )

    # session message to display on redirected view
    messages.add_message(
        request,
        messages.INFO,
        unicode(strings.CIRCUIT_REMIXED_SUCCES % {
            'route': remixed_circuit.name
            })
    )

    # Register notifiable event
    NotifiableEvent.register_event_circuit_remixed(
        owner=request.user,
        remixed_circuit=remixed_circuit,
        original_circuit=circuit,
        timestamp=remixed_circuit.created
    )

    return HttpResponseRedirect(
        reverse('circuit_edit', kwargs={'circuit_id': remixed_circuit.id})
    )


@login_required
@require_POST
def create_circuit(request):
    new_circuit_form = CircuitForm(request.POST)
    if new_circuit_form.is_valid():
        objects = new_circuit_form.process_objects(author=request.user)
        circuit = objects['circuit']
    else:
        errors = error_list_from_form(new_circuit_form)
        content = json_error_document(errors)
        return HttpResponseBadRequest(
            content=content,
            content_type='application/json'
        )

    # Register notifiable event
    NotifiableEvent.register_event_circuit_created(
        owner=request.user,
        circuit=circuit,
        timestamp=circuit.created
    )

    return HttpResponseRedirect(
        reverse('circuit_edit', kwargs={'circuit_id': circuit.id})
    )


@login_required
def edit_circuit(request, circuit_id):
    # Retrieve circuit and get attributes
    circuit = get_object_or_404(Circuit, pk=circuit_id)

    if request.user.id != circuit.author_id:
        return render(request,
                      settings.FORBIDDEN_TEMPLATE, {})

    stops = []
    for stop in circuit.circuit_stops.order_by('-id').all():
        data = stop.get_data()
        data['json'] = json.dumps(data)
        stops.append(data)

    circuit_stops_count = circuit.circuit_stops.count

    circuit_update_form = CircuitUpdateControllerForm(
        auto_id=False,
        initial={'adult_content': circuit.adult_content},
    )
    circuit_picture_form = CircuitPictureControllerForm(auto_id=False)
    stop_creation_form = CircuitStopCreationControllerForm(auto_id=False)
    place_types = PlaceType.objects.order_by('name').all()

    return render(request,
        'circuits/circuit_edit.html',
        {
            'circuit': circuit,
            'stops': stops,
            'circuit_stops_count': circuit_stops_count,
            'circuit_update_form': circuit_update_form,
            'circuit_picture_form': circuit_picture_form,
            'stop_creation_form': stop_creation_form,
            'empty_stop': {},
            'place_types': place_types,
            'STATIC_MAPS_ROOT': settings.STATIC_MAPS_ROOT,
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY
        },
    )


def circuit_category_listing(request, category_slug, gmac_slug=None):
    """
    Displays the first 10 circuits of a category
    """
    # Find GMAC
    gmacs = None
    if gmac_slug is not None:
        try:
            gmacs = GMAC.objects.filter(slug=gmac_slug)
        except GMAC.DoesNotExist:
            pass

    cpp = circuit_settings.DEFAULT_CIRCUITS_LIMIT

    try:
        category_value = CIRCUIT_CATEGORY_CHOICES.get_value(
            category_slug.upper()
        )
    except KeyError:
        raise Http404

    categories = circuit_category_list()
    category = CircuitCategory(category_value)

    params = {}

    params['category'] = category_value

    gmac_get_short_formatted_name = None
    if gmacs is not None:
        params['pk__in'] = [ c.pk for c in Circuit.filter_by_gmacs(gmacs)]
        gmac_get_short_formatted_name = gmacs[0].get_short_formatted_name()

    if request.is_ajax():
        page = request.POST.get('page', None)
        if page is not None:
            page = int(page)
        else:
            error_doc = OrderedDict()
            error_doc['error'] = 'Missing POST parameter: page'
            return HttpResponse(
                content=render_as_json(error_doc),
                content_type='application/json'
            )

        response = {
            'page': int(page) + 1
        }

        circuits = Circuit.objects.available().filter(**params).order_by(
            '-modified'
        )[page * cpp: (page + 1) * cpp]

        if circuits:
            html_response = u''

            for circuit in circuits:
                html_response += render_to_string(
                    'circuits/circuit_list_item.html',
                    {'circuit': circuit, 'user': request.user}
                )
            response['raw_html'] = html_response

        else:
            response['hide_button'] = True

        return HttpResponse(
            content=json.dumps(response),
            content_type='application/json'
        )

    # FIXME circuits filter should also include location of user
    circuits = Circuit.objects.available().filter(**params).order_by(
        '-modified'
    )[:cpp]

    return render(request,
        'circuits/categories.html',
        {
            'categories': categories,
            'category': category,
            'selected_category': category_value,
            'category_slug': category_slug,
            'is_preferred_category': category.is_followed(request.user),
            'circuits': circuits,
            'topbar_item': 'explore',
            'page_type': 'category',
            'gmacs': gmacs,
            'gmac_slug': gmac_slug,
            'STATIC_MAPS_ROOT': settings.STATIC_MAPS_ROOT,
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
            'gmac_get_short_formatted_name': gmac_get_short_formatted_name,
        },
    )


@login_required
def my_circuits_list_view(request):
    """
    Show a list of circuits whos author is request.user, this view
    assumes that my route is only show when the user is logged in
    and not anonymous
    """

    circuits_per_page = circuit_settings.DEFAULT_CIRCUITS_LIMIT

    if request.is_ajax():
        page = request.POST.get('page', None)
        if page is not None:
            page = int(page)
        else:
            return HttpResponse(
                json.dumps({'error': 'Missing POST parameter: page'}),
                mimetype='application/json')

        response = {
            'page': int(page) + 1
            }

        circuits = Circuit.objects.filter(
            author=request.user
            ).order_by(
            'published',
            '-created',
            )[circuits_per_page * page: circuits_per_page * (page + 1)]

        if circuits:
            html_response = u''

            for circuit in circuits:
                html_response += render_to_string(
                    'circuit/circuit_list_item.html',
                    {'circuit': circuit, 'user': request.user})
            response['raw_html'] = html_response
        else:
            response['hide_button'] = True

        return HttpResponse(json.dumps(response),
            mimetype='application/json')


    circuits = Circuit.objects.filter(author=request.user) \
        .order_by('published', '-created')[:circuits_per_page] \
        .all()

    # First time here? Force the user to register some prefered categories
    first_time = False
    categories_form = None
    if not circuits:
        user_categories = request.user.categories.all()
        if not user_categories:
            first_time = True
            categories_form = make_categories_form()

    return render(request,
        'circuits/mycircuits.html',
        {
            'circuits': circuits,
            'topbar_item': 'my_routes',
            'STATIC_MAPS_ROOT': settings.STATIC_MAPS_ROOT,
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
            'first_time': first_time,
            'categories_form': categories_form,
        },
    )


def circuit_detail(request, circuit_id, slug=None):
    """
    Shows the detail of a circuit
    """
    if slug is None:
        circuit = get_object_or_404(
            Circuit,
            pk=circuit_id,
        )
    else:
        circuit = get_object_or_404(
            Circuit,
            pk=circuit_id,
            slug=slug
        )

    # In case the session user has not agreed to watch adult content
    if circuit.adult_content:
        adult_content = request.session.get('adult_content', False)
        if adult_content is False and circuit.author != request.user :
            return HttpResponseRedirect(
                reverse('adult_content_agreement', args=(circuit_id,))
            )

    circuit_stops = circuit.circuit_stops.all().order_by('position')
    circuit_stops_count = circuit.circuit_stops.count

    circuit_comments = circuit.comments.all()

    circuit_vote = 0
    circuit_vote_str = ''
    is_author = False
    is_favorite = False
    done_places = []

    if request.user.is_authenticated():
        is_author = circuit.author == request.user
        is_favorite = circuit in request.user.userprofile.favorites.all()
        circuit_vote = circuit.get_vote(request.user)
        circuit_vote_str = 'up' if circuit_vote == 1 else \
            'down' if circuit_vote == -1 else ''

        #TODO Improve this?
        places_ids = [s.place_id for s in circuit_stops]
        done_places = request.user.done_place_records \
            .filter(place__in=places_ids).all()
        done_places = [dp.place_id for dp in done_places]

    # Send event signal
    circuit_visited.send(sender=circuit, request=request)

    embed_value = request.GET.get('embedded', False)

    if embed_value not in EMBEDDING_FAIL_VALUES:
        return render(
            request,
            'circuits/embedded_circuit_detail.html',
            {
                'circuit': circuit,
                'circuit_stops': circuit_stops,
                'circuit_stops_count': circuit_stops_count,
                'done_places': done_places,
                'is_author': is_author,
                'is_favorite': is_favorite,
                'circuit_vote': circuit_vote,
                'circuit_vote_str': circuit_vote_str,
                'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
                'domain': settings.SITE_PREFIX,
            }
        )

    return render(
        request,
        'circuits/circuit_detail.html',
        {
            'circuit': circuit,
            'circuit_stops': circuit_stops,
            'circuit_stops_count': circuit_stops_count,
            'comments': circuit_comments,
            'done_places': done_places,
            'site_prefix': settings.SITE_PREFIX,
            'is_author': is_author,
            'is_favorite': is_favorite,
            'circuit_vote': circuit_vote,
            'circuit_vote_str': circuit_vote_str,
            'STATIC_MAPS_ROOT': settings.STATIC_MAPS_ROOT,
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
        }
    )

@login_required
def set_favorite_cats(request):
    if request.method == 'POST':
        categories = request.POST.getlist('category', [])
        # retrieve user
        user = request.user
        # validate categories and trimm not valid
        valid_categories = []
        for cat in categories:
            if CIRCUIT_CATEGORY_CHOICES.has_value(int(cat)):
                valid_categories.append(cat)

        # delete all previously followed categories
        prev_cats = user.categories.all()
        for followed_cat in prev_cats:
            # Shoot remove favorite signal
            category_unfollow.send(
                sender=user,
                category_id=followed_cat.category
            )
            followed_cat.delete()


        for cat in valid_categories:
            # Create CircuitCategoryFollow object
            follow_record = CircuitCategoryFollow(
                user=user,
                category=cat
            )
            # Add favorite
            user.categories.add(follow_record)
            # Shoot follow signal
            category_follow.send(sender=user, category_id=cat)

        # redirect to user_profile
        return redirect('website.views.show_home')

    uproxy = CircuitRelatedUserProxy.from_user(request.user)
    fav_cats = uproxy.get_favorite_circuit_categories()
    non_fav_cats = uproxy.get_non_favorite_circuit_categories()
    initial = {}
    for cat in fav_cats:
        initial[cat] = True
    for cat in non_fav_cats:
        initial[cat] = False

    Form = make_categories_form()
    form = Form(initial)
    return render(request,
        'profile/cats.html',
        {
            'form': form,
            'initial': initial,
        }
    )


def stop_detail(request, stop_id):
    try:
        stop = CircuitStop.objects.get(pk=stop_id)
    except CircuitStop.DoesNotExist:
        raise Http404

    is_done = False
    if request.user.is_authenticated():
        is_done = request.user.done_place_records \
            .filter(place__pk=stop.place.pk).count()

    return render(request,
        'circuits/stop_detail.html',
        {
            'stop': stop,
            'is_done': is_done,
            'STATIC_MAPS_ROOT': settings.STATIC_MAPS_ROOT,
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
        },
    )


@login_required
def stop_edit(request, stop_id):
    """
    Web view for editing a CircuitStop, has an API counterpart
    """
    stop = get_object_or_404(CircuitStop, pk=stop_id)

    if request.method == 'POST':
        form = StopEditForm(request.POST, request.FILES, instance=stop)
        if form.is_valid():
            form.save()
            # Register notifiable event
            NotifiableEvent.register_event_circuit_updated(
                owner=request.user,
                circuit=stop.circuit
            )
            return HttpResponse(stop.to_json())

    form = StopEditForm(instance=stop)

    return render(request,
        'circuits/stop_edit.html',
        {
            'form': form,
        }
    )


@login_required
@require_POST
def stop_delete(request, stop_id):
    """
    Deletes a stop, validating that request.user is the author of the circuit
    """
    if CircuitStop.objects.filter(pk=stop_id).exists():
        stop = CircuitStop.objects.get(pk=stop_id)
    else:
        raise Http404

    if stop.circuit.author == request.user:
        redirect_url = stop.circuit.get_update_url()
        stop.delete()
        if request.is_ajax:
            return HttpResponse(json.dumps({'redirect': redirect_url}))
        # If succesfully, redirect to circuit
        return HttpResponseRedirect(redirect_url)
    else:
        raise HttpResponseForbidden


@login_required
@require_POST
def delete_circuit(request, circuit_id):
    """
    Deletes a circuit and recursively its stops
    """
    try:
        circuit = Circuit.objects.get(pk=circuit_id)
    except Circuit.DoesNotExist:
        raise Http404

    if circuit.author == request.user:
        # delete all its stops
        for stop in circuit.circuit_stops.all():
            stop.delete()
        circuit.delete()
        redirect_url = reverse('mycircuits')
        # If succesfully, redirect to home
        return HttpResponseRedirect(redirect_url)
    else:
        # in case user is not allowed to erase the route
        raise HttpResponseForbidden


@require_POST
def circuit_pagination(request):
    """
    The POST parameter indicates the type of search
    pagination-type: recommendation/category
    pagination: page to serve
    total-circuits: upper bound
    """
    page_type = request.POST.get('page_type', None)
    page = request.POST.get('page', None)
    category_type = request.POST.get('category_type', None)

    if (page is not None) and (page_type is not None):
        page = int(page)
        page_type = page_type
    else:
        return HttpResponse(json.dumps({'error': 'No page or page_type'}),
                mimetype='application/json')

    # page_type category requires category_type
    if page_type == 'category':
        if category_type is None:
            return HttpResponse(json.dumps(
                {'error': 'page_type category requires category_type'}),
                mimetype='application/json')

    response = {
        'page': int(page) + 1
    }

    circuits_per_page = circuit_settings.DEFAULT_CIRCUITS_LIMIT

    if page_type == 'recommendation':
        circuits = Circuit.objects.all().order_by('-modified'
            )[circuits_per_page * page: circuits_per_page * (page + 1)]
    elif page_type == 'category':
        circuits = Circuit.objects.filter(category=category_type
                ).order_by('-modified'
                )[circuits_per_page * page: circuits_per_page * (page + 1)]

    if circuits:
        html_response = u''
        for circuit in circuits:
            html_response += render_to_string('circuits/circuit_list_item.html',
                    {'circuit': circuit, 'user': request.user})
        response['raw_html'] = html_response
    else:
        response['hide_button'] = True

    return HttpResponse(json.dumps(response), mimetype='application/json')


@login_required
def adult_content_agreement(request, circuit_id):
    """
    View that shows the user to agree with adult content
    """
    return render(request, 
        'circuits/adult_content_agreement.html', 
        {
            'circuit_id': circuit_id,
        }
    )

@login_required
def adult_content_agreement_agree(request, circuit_id):
    """
    User agrees to watch adult content
    """
    request.session['adult_content'] = True
    return HttpResponseRedirect(
        reverse('circuit_detail_without_slug', args=(circuit_id,))
    )
