# -*- coding: utf-8 -*-

import simplejson as json
from ordereddict import OrderedDict

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.comments.models import Comment
from django_extensions.db.fields import AutoSlugField
from django.conf import settings
from django.core.urlresolvers import reverse
from sorl.thumbnail.fields import ImageField

from common.models import AuditableModel, AuditableManager
from common.datastructures import Enumeration
from common.utils.pictures import uuid_based_picture_name
from common import mixins

from visits.models import Visit
from places.models import Place
from topics.models import Topic
from circuits import constants, strings
from circuits.utils import CircuitCategory
from circuits.utils import circuit_category_list
from circuits.signals import (circuit_remixed, circuit_remix_deleted, 
                              circuit_created, circuit_deleted, circuit_updated)
from stats.querying import RedisStatsQuery


class CircuitManager(AuditableManager):

    def available(self):
        return self.filter(published=True)


class Circuit(mixins.ObjectWithPictureMixin, AuditableModel):
    """
    Circuit class, collection of places and topics
    """

    name = models.CharField(
        verbose_name=strings.CIRCUIT_NAME,
        max_length=256,
    )

    slug = AutoSlugField(
        verbose_name=strings.CIRCUIT_SLUG,
        populate_from='name',
        unique=False,
        editable=False,
    )

    remixed_from = models.ForeignKey('self',
        verbose_name=strings.CIRCUIT_REMIXED_FROM,
        blank=True,
        null=True,
    )

    category = models.IntegerField(
        verbose_name=strings.CIRCUIT_CATEGORY,
        choices=constants.CIRCUIT_CATEGORY_CHOICES,
    )

    description = models.CharField(
        verbose_name=strings.CIRCUIT_DESCRIPTION,
        max_length=512,
        blank=True,
        null=True,
    )

    author = models.ForeignKey(User,
        verbose_name=strings.CIRCUIT_AUTHOR,
    )

    rating = models.FloatField(
        verbose_name=strings.CIRCUIT_RATING,
        default=0.0,
    )

    picture = ImageField(
        verbose_name=strings.CIRCUIT_PICTURE,
        upload_to=uuid_based_picture_name('pictures/circuits'),
        blank=True,
        null=True,
    )

    # Relationship with Topic
    topics = models.ManyToManyField(Topic,
        verbose_name=strings.CIRCUIT_TOPICS,
        related_name='circuits',
        null=True,
        blank=True,
    )

    visits = generic.GenericRelation(Visit,
        verbose_name=strings.CIRCUIT_VISITS,
    )

    published = models.BooleanField(
        verbose_name=strings.CIRCUIT_PUBLISHED,
        default=True,
    )

    highlighted = models.BooleanField(
        verbose_name=strings.CIRCUIT_HIGHLIGHTED,
        default=False,
    )

    source = models.PositiveIntegerField(
        choices=constants.CIRCUIT_SOURCE_CHOICES,
        default=constants.CIRCUIT_SOURCE_CHOICES.WORLDRAT_USERS,
        blank=True,
        null=True,
    )

    adult_content = models.BooleanField(
        verbose_name=strings.CIRCUIT_ADULT_CONTENT,
        default=False,
    )

    #Relation to comments model
    comments = generic.GenericRelation(Comment, object_id_field='object_pk')

    objects = CircuitManager()

    def __unicode__(self):
        return u'%s' % (self.name,)

    def delete(self):
        """ Extension of parent delete method """ 
        # in case circuit is remix of some other circuit
        if self.remixed_from:
            # Send signal to update Redis DB
            circuit_remix_deleted.send(
                sender=self, 
                remixed_circuit_id=self.pk
            )
        # Send signal to update Redis DB
        circuit_deleted.send(sender=self)
        # call parent method
        super(Circuit, self).delete()

    def save(self):
        """ Extension of parent save method """
        # Signal to verify updated data
        circuit_updated.send(sender=self)
        # if circuit has 0 stops make published = False
        if self.circuit_stops.count() == 0:
            self.published = False
        else:
            self.published = True
        # Call parent method
        super(Circuit, self).save()
        # Send signal to update Redis DB
        circuit_created.send(sender=self)
        # position fixer method
        self.fix_stops_position()

    class Meta:
        verbose_name = strings.CIRCUIT_VERBOSE_NAME
        verbose_name_plural = strings.CIRCUIT_VERBOSE_NAME_PLURAL

    def stats(self):
        """ Returns circuit stats obtained from Redis """
        R = RedisStatsQuery()
        return{
            'visit_count': R.circuit_visits(self.pk),
            'favorite_count': R.circuit_fav_count(self.pk),
            'remix_count': R.circuit_remix_count(self.pk),
            #'comment_count': self.comments.count()
        }

    def fix_stops_position(self):
        stops = []
        for stop in self.circuit_stops.all():
            stops.append(stop)
        # super magical sorting function
        stops.sort(key=lambda CircuitStop: CircuitStop.place.coordinates.x)
        # set new position to stop
        counter = 1
        for stop in stops:
            stop.position = counter
            stop.save()
            counter += 1

    def get_data(self):
        pic = self.get_picture(settings.THUMB_SMALL_SIZE)
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'category_display': self.get_category_display(),
            'description': self.description,
            'adult_content': self.adult_content,
            'picture_url': pic['url'],
            'picture_ratio_hw': pic['ratio_hw'],
        }

    def to_json(self):
        """Return a JSON representation for easy storage and reuse in the
        template.
        """
        return json.dumps(self.get_data())

    def get_update_url(self):
        return reverse('circuit_update_controller_resource',
            kwargs={'circuit_id': self.id})

    @property
    def verbose_category(self):
        return unicode(constants.CIRCUIT_CATEGORY_CHOICES[self.category][1])

    def get_visitors(self):
        """
        Returns a QuerySet containing all the User objects
        who visited this circuit
        """
        user_id_list = []

        for uv in self.visits.all():
            if uv.visitor.id not in user_id_list:
                user_id_list.append(uv.visitor.id)

        return User.objects.filter(id__in=user_id_list)

    def get_places(self):
        """
        Returns a QuerySet containing the related places
        """
        raw_places = self.circuit_stops.values('place')
        places = []
        for elem in raw_places:
            places.append(elem['place'])

        return Place.objects.filter(pk__in=places)

    def get_raters(self):
        """
        Returns a QuerySet containing the Users that rated this circuit
        """
        raw_users = self.circuit_ratings.values('user')
        users = []
        for elem in raw_users:
            users.append(elem['user'])

        return User.objects.filter(id_in=users)

    def get_circuit_rating(self, user):
        try:
            circuit_rating = CircuitRating.objects.get(
                circuit=self,
                user=user
            )
            return circuit_rating
        except CircuitRating.DoesNotExist:
            return None

    def register_vote(self, user, vote):
        cr = self.get_circuit_rating(user)
        is_pending = (vote == CircuitRating.VOTE_TYPE_CHOICES.PENDING)

        if cr:
            print cr.vote, vote
            if is_pending:
                cr.delete()
            elif cr.vote != vote:
                cr.vote = vote
                cr.save()
            return

        # Add only if it's an upvote or a downvote
        if is_pending:
            return
        cr = CircuitRating(
            circuit=self,
            user=user,
            vote=vote,
        )
        cr.save()

    def register_upvote(self, user):
        vote = CircuitRating.VOTE_TYPE_CHOICES.UPVOTE
        return self.register_vote(user, vote)

    def register_downvote(self, user):
        vote = CircuitRating.VOTE_TYPE_CHOICES.DOWNVOTE
        return self.register_vote(user, vote)

    def reset_vote(self, user):
        vote = CircuitRating.VOTE_TYPE_CHOICES.PENDING
        return self.register_vote(user, vote)

    def get_vote(self, user):
        """Returns 1, -1 or 0 according if the vote of `user` is an upvote,
        downvote or none.
        """
        cr = self.get_circuit_rating(user)
        if not cr:
            return 0
        if cr.vote == CircuitRating.VOTE_TYPE_CHOICES.UPVOTE:
            return 1
        if cr.vote == CircuitRating.VOTE_TYPE_CHOICES.DOWNVOTE:
            return -1
        return 0

    def arrange_positions(self, uuid_list):
        missing = []
        current = OrderedDict()
        qs = self.circuit_stops.all()

        for cs in qs:
            current[cs.uuid] = cs

        found = 0
        unspecified = 0
        updated = 0
        new_order = []

        position = 0

        # Update position of circuit stops included
        # in the list of UUIDs
        for uuid in uuid_list:
            position += 1
            if uuid in current:
                found += 1
                cs = current[uuid]
                if cs.position != position:
                    cs.position = position
                    cs.save()
                    updated += 1
                del(current[uuid])
                new_order.append(uuid)
            else:
                missing.append(uuid)

        # Remaining circuit stops
        for uuid in current:
            position += 1
            cs = current[uuid]
            if cs.position != position:
                cs.position = position
                cs.save()
                updated += 1
                unspecified += 1
            del(current[uuid])
            new_order.append(uuid)

        results = OrderedDict()
        results['found'] = found
        results['unspecified'] = unspecified
        results['updated'] = updated
        results['new_order'] = new_order
        results['missing'] = missing

        return results

    def calculate_rating(self):
        """
        sets the member rating to the % of upvotes and downvotes
        """
        all_ct_ratings = self.circuit_ratings.values('vote')

        if len(all_ct_ratings):
            all_votes = []
            for vote in all_ct_ratings:
                all_votes.append(vote['vote'])

            upvotes = 0
            for vote in all_votes:
                if vote == 1:
                    upvotes += 1

            self.rating = (upvotes * 100) / len(all_votes)
            self.save()

    def get_absolute_url(self):
        return reverse(
            'circuit_detail_with_slug',
            #'circuit_detail_without_slug',
            kwargs={
                'circuit_id': self.pk,
                'slug': self.slug,
            }
        )

    def get_restful_url(self):
        return "%s%s" % (
            settings.API_V1_PREFIX.rstrip('/'),
            reverse('circuit_resource', kwargs={'circuit_id': self.id})
        )

    def get_restful_link_metadata(self):
        metadata = OrderedDict()
        metadata['href'] = self.get_restful_url()
        metadata['rel'] = 'alternate'
        metadata['title'] = self.name
        metadata['type'] = 'application/json'
        return metadata

    def get_last_position(self):
        """ Checks for greater position
            ad returns the integer of it
        """
        return self.circuit_stops.count()

    def is_authorized(self, user):
        if self.author == user:
            return True
        elif user.is_staff:
            return True
        return False

    # TODO: method not needed, not allowing default circuit now
    @staticmethod
    def create_default_circuit(author):
        circuit = Circuit(
            name=strings.DEFAULT_CIRCUIT_NAME,
            category=constants.DEFAULT_CIRCUIT_CATEGORY,
            author=author
        )
        circuit.save()
        return circuit

    def get_category_object(self):
        return CircuitCategory(self.category)

    @staticmethod
    def delete_empty_citcuits():
        """
        deletes all circuits with no stops associated to it, created
        to wipe nexstop empty circuits
        """
        all_cts = Circuit.objects.all()
        for ct in all_cts:
            if len(ct.get_places()) == 0:
                ct.delete()

    def remix(
            self, 
            new_author, 
            new_title, 
            new_category, 
            new_description=None,
            adult_content=False
        ):
        """
        Returns a Copy of the current circuit and stops with a new id, unsaved.
        new_author: UserProfile
        """
        new_circuit = Circuit()
        new_circuit.name = new_title
        new_circuit.author = new_author
        new_circuit.category = new_category
        new_circuit.description = new_description
        new_circuit.picture = self.picture
        if adult_content:
            new_circuit.adult_content = True

        if self.remixed_from:
            new_circuit.remixed_from = self.remixed_from
        else:
            new_circuit.remixed_from = self

        new_circuit.save()
        for stop in self.circuit_stops.all():
            new_stop = CircuitStop()
            new_stop.circuit = new_circuit
            new_stop.place = stop.place
            new_stop.description = u''
            new_stop.position = stop.position
            new_stop.picture = stop.picture
            new_stop.save()

        # Send signal to update Redis DB
        circuit_remixed.send(
            sender=self, 
            remixed_circuit_id=new_circuit.pk
        )
        return new_circuit

    def get_coordinates_box(self):
        min_lat = None
        max_lat = None
        min_lng = None
        max_lng = None
        # Get min and max latitude
        for stop in self.circuit_stops.all():
            lat = stop.lat
            lng = stop.lng
            # Minimal latitude
            if min_lat is None:
                min_lat = lat
            elif lat < min_lat:
                min_lat = lat
            # Maximal latitude
            if max_lat is None:
                max_lat = lat
            elif lat > max_lat:
                max_lat = lat
            # Minimal longitude
            if min_lng is None:
                min_lng = lng
            elif lng < min_lng:
                min_lng = lng
            # Maximal longitude
            if max_lng is None:
                max_lng = lng
            elif lng > max_lng:
                max_lng = lng
        result = OrderedDict()
        result['lat'] = OrderedDict()
        result['lat']['min'] = min_lat
        result['lat']['max'] = max_lat
        result['lng'] = OrderedDict()
        result['lng']['min'] = min_lng
        result['lng']['max'] = max_lng
        return result

    def get_followers(self):
       return [profile.user for profile in self.follower_profiles.all()]

    @staticmethod
    # FIXME: @mathiasbc returns duplicated circuits, must fix it
    def filter_by_gmac(gmac):
        """ gmac = GMAC instance """
        stops = CircuitStop.filter_by_gmac(gmac)
        cts = Circuit.objects.filter(circuit_stops__in=stops)
        circuits = []
        for ct in cts:
            if ct not in circuits:
                circuits.append(ct)
        return circuits

    @staticmethod
    def filter_by_gmacs(gmacs):
        stops = []
        for gmac in gmacs:
            stops += Circuit.filter_by_gmac(gmac)
        return stops

class CircuitStop(mixins.ObjectWithPictureMixin, models.Model):
    """
    Relation between Circuit a Places
    """

    circuit = models.ForeignKey(Circuit,
        verbose_name=strings.CIRCUIT_STOP_CIRCUIT,
        related_name='circuit_stops'
    )

    place = models.ForeignKey(Place,
        verbose_name=strings.CIRCUIT_STOP_PLACE,
        related_name='circuit_stops',
    )

    description = models.CharField(
        verbose_name=strings.CIRCUIT_STOP_DESCRIPTION,
        max_length=400,
        blank=True,
        null=True,
    )

    position = models.PositiveIntegerField(
        verbose_name=strings.CIRCUIT_STOP_POSITION,
        default=constants.DEFAULT_CIRCUIT_STOP_POSITION,
    )

    picture = ImageField(
        verbose_name=strings.CIRCUIT_PICTURE,
        upload_to=uuid_based_picture_name('pictures/circuit_stops'),
        blank=True,
        null=True,
    )

    def __unicode__(self):
        return strings.CIRCUIT_STOP_UNICODE % {
            'place': self.place.name,
            'circuit': self.circuit.name
        }

    @property
    def lat(self):
        if self.place:
            return self.place.lat
        else:
            return None

    @property
    def lng(self):
        if self.place:
            return self.place.lng
        else:
            return None

    def get_data(self):
        update_url = self.get_update_url()
        delete_url = self.get_delete_url()
        place_type = self.place.get_place_type()

        pic = self.get_picture(settings.THUMB_SMALL_SIZE)
        return {
            'id': self.id,
            'place_id': self.place.place_id,
            'name': self.place.name,
            'picture_url': pic['url'],
            'picture_ratio_hw': pic['ratio_hw'],
            'description': self.description,
            'address': self.place.address,
            'crossStreet': self.place.crossStreet,
            'update_url': update_url,
            'delete_url': delete_url,
            'lat': str(self.place.lat).replace(',', '.'),
            'lng': str(self.place.lng).replace(',', '.'),
            'place_type': place_type.shortName,
            'place_type_id': place_type.place_type_id,
        }

    def to_json(self):
        """Return a JSON representation for easy storage and reuse in the
        template.
        """
        return json.dumps(self.get_data())

    def get_restful_url(self):
        return '%s%s' % (
            settings.API_V1_PREFIX.rstrip('/'),
            reverse('circuit_stop_resource',
                kwargs={
                    'circuit_id': self.circuit.id,
                    'stop_id': self.id,
                }
            )
        )

    def get_restful_link_metadata(self, rel='alternate'):
        metadata = OrderedDict()
        metadata['href'] = self.get_restful_url()
        metadata['rel'] = rel
        metadata['title'] = self.place.name
        metadata['type'] = 'application/json'
        return metadata

    def get_update_url(self):
        return reverse('stop_edit', kwargs={'stop_id': self.id})

    def get_delete_url(self):
        return reverse('stop_delete', kwargs={'stop_id': self.id})

    def save(self, *args, **kwargs):
        print len(self.description)
        super(CircuitStop, self).save(*args, **kwargs)

    @staticmethod
    def filter_by_gmac(gmac):
        params = {}
        gmac_id_list = gmac.get_id_list_from_redis(gmac.pk)
        params['place__locality__pk__in'] = gmac_id_list
        return CircuitStop.objects.filter(**params)

    class Meta:
        verbose_name = strings.CIRCUIT_STOP_VERBOSE_NAME
        verbose_name_plural = strings.CIRCUIT_STOP_VERBOSE_NAME_PLURAL


class CircuitRating(models.Model):
    """
    Relation between User and Circuit
    """

    VOTE_TYPE_CHOICES = Enumeration([
        (1, 'UPVOTE', strings.VOTE_TYPE_UPVOTE),
        (0, 'PENDING', strings.VOTE_TYPE_PENDING),
        (-1, 'DOWNVOTE', strings.VOTE_TYPE_DOWNVOTE)
    ])

    # Relationship with User
    user = models.ForeignKey(User,
        verbose_name=strings.RATING_USER,
        related_name='circuit_ratings'
    )

    # Relationship with Circuit
    circuit = models.ForeignKey(Circuit,
        verbose_name=strings.RATING_CIRCUIT,
        related_name='circuit_ratings'
    )

    vote = models.SmallIntegerField(
        verbose_name=strings.RATING_VOTE,
        choices=VOTE_TYPE_CHOICES,
        default=VOTE_TYPE_CHOICES.PENDING
    )

    def __unicode__(self):
        return self.get_vote_display()

    class Meta:
        verbose_name = strings.RATING_VERBOSE_NAME
        verbose_name_plural = strings.RATING_VERBOSE_NAME_PLURAL

    def is_upvote(self):
        return self.vote == self.VOTE_TYPE_CHOICES.UPVOTE

    def is_downvote(self):
        return self.vote == self.VOTE_TYPE_CHOICES.DOWNVOTE

    def is_pending(self):
        return self.vote == self.VOTE_TYPE_CHOICES.PENDING


class CircuitRelatedUserProxy(User):
    """
    Returns a QuerySet of rated circuits for the given user
    User = user.id
    """
    class Meta:
        proxy = True

    @staticmethod
    def from_user(user):
        return CircuitRelatedUserProxy.objects.get(
            username=user.username
        )

    def get_user(self):
        try:
            return User.objects.get(pk=self.id)
        except User.DoesNotExist:
            return None

    def is_following_cat(self, cat_id):
        user = self.get_user()
        if user is None:
            return False

        if CircuitCategoryFollow.objects.filter(user=user,
                                                category=cat_id).exists():
            return True
        else:
            return False

    def follow_category(self, cat_id):
        user = self.get_user()
        if user is None:
            return False
        try:
            record = CircuitCategoryFollow.objects.get(
                user=user,
                category=cat_id
                )
            return False
        except CircuitCategoryFollow.DoesNotExist:
            record = CircuitCategoryFollow(
                user=user,
                category=cat_id
            )
            record.save()
            return True

    def unfollow_category(self, cat_id):
        user = self.get_user()
        if user is None:
            return False
        try:
            record = CircuitCategoryFollow.objects.get(
                user=user,
                category=cat_id
            )
            record.delete()
            return True
        except CircuitCategoryFollow.DoesNotExist:
            return False

    def get_rated_circuits(self):
        """
        Returns a QuerySet with the circuits that user rated
        """
        rated_circuits = CircuitRating.objects.filter(
                user__id=self.id
            )

        rated_circuit_id_list = [
            rating.circuit.id for rating in rated_circuits
        ]
        return Circuit.objects.filter(id__in=rated_circuit_id_list)

    def get_upvoted_circuits(self):
        """
        Returns a QuerySet with circuits that user upvoted
        """
        upvoted = CircuitRating.objects.filter(
            user__id=self.id).filter(
            vote=1
        )

        upvoted_cts = []
        for ct in upvoted:
            upvoted_cts.append(ct.circuit)

        return upvoted_cts

    def get_visited_circuits(self):
        """
        Returns a QuerySet with the circuits that user visited
        """
        visited_circuits = Visit.objects.filter(
            visitor__id=self.id
        )

        vtd_circuits_ids = []

        for ct in visited_circuits:
            if ct.object_id not in vtd_circuits_ids:
                vtd_circuits_ids.append(ct.object_id)

        return Circuit.objects.filter(id__in=vtd_circuits_ids)

    def get_favorite_circuit_categories(self):
        results = []
        records = CircuitCategoryFollow.objects.filter(user=self.get_user())
        for r in records:
            results.append(r.get_category_object())
        return results

    def get_favorite_categories_ids(self):
        """
        returns a list of the id of categories marked as follow by user
        """
        results = []
        records = CircuitCategoryFollow.objects.filter(user=self.get_user())
        for r in records:
            results.append(r.category)
        return results

    def get_non_favorite_circuit_categories(self):
        results = []
        all_cats = circuit_category_list()
        favs_id_list = [c.id for c in self.get_favorite_circuit_categories()]
        for cat in all_cats:
            if cat.id not in favs_id_list:
                results.append(cat)
        return results

    def simple_recsys(self, top_n=-1):
        """
        simple recommendation system based on visits per circuit on categories
        chosen by user.
        returns a QuerySet of circuits
        top_n = -1 returns all the Queryset
        """
        import operator
        # get categories user likes
        user = self.get_user()
        R = RedisStatsQuery(user)
        fav_cats = self.get_favorite_categories_ids()
        # retrieve all circuits ids from favorite categories
        # ======================================================================
        # FIXME: use this block when Redis has the necessary key
        #posible_circuits = []
        #for cat in fav_cats:
        #    posible_circuits.extend(R.category_in_circuits(cat))
        # ======================================================================
        posible_circuits = Circuit.objects.filter(category__in=fav_cats)
        rec_vec = {}
        # append all visits to a dictionary with key=circuit.id
        for ct in posible_circuits:
            rec_vec[ct.id] = R.circuit_visits(ct.id)
        # sort the rec_vec in order of visits
        sorted_vec = sorted(
            rec_vec.iteritems(),
            key=operator.itemgetter(1),
            reverse=True
        )
        # get ordered circuits ids
        ct_ids = []
        for circuit in sorted_vec:
            ct_ids.append(circuit[0])

        if top_n == -1:
            return Circuit.objects.filter(pk__in=ct_ids)
        else:
            return Circuit.objects.filter(pk__in=ct_ids)[:top_n]


class CircuitCategoryFollow(AuditableModel):
    """
    Relation between user and category
    """
    # Relationship with User
    user = models.ForeignKey(User,
        verbose_name=strings.CCF_USER,
        related_name='categories',
    )

    # Category itself
    category = models.PositiveIntegerField(
        verbose_name=strings.CCF_CATEGORY,
        choices=constants.CIRCUIT_CATEGORY_CHOICES,
    )

    def __unicode__(self):
        return strings.CCF_UNICODE % {
            'user': self.user.get_full_name(),
            'category': self.get_category_display()
        }

    def get_category_object(self):
        return CircuitCategory(self.category)

    class Meta:
        verbose_name = strings.CCF_VERBOSE_NAME
        verbose_name_plural = strings.CCF_VERBOSE_NAME_PLURAL
        unique_together = (('user', 'category'),)
