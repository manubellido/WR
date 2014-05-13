# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

CIRCUIT_VERBOSE_NAME = _(u'Routes')
CIRCUIT_VERBOSE_NAME_PLURAL = _(u'Routes')
CIRCUIT_NAME = _(u'Route name')
CIRCUIT_SLUG = _(u'Slug')
CIRCUIT_AUTHOR = _(u'Route author')
CIRCUIT_RATING = _(u'Route rating')
CIRCUIT_CATEGORY = _(u'Route category')
CIRCUIT_PICTURE = _(u'Route picture')
CIRCUIT_TOPICS = _(u'Topics')
CIRCUIT_VISITS = _(u'Visits')
CIRCUIT_PUBLISHED = _(u'Published')
CIRCUIT_HIGHLIGHTED = _(u'Highlighted route')
CIRCUIT_DESCRIPTION = _(u'Route description')
CIRCUIT_REMIXED_FROM = _(u'Original route')
CIRCUIT_ADULT_CONTENT = _(u'Adult content')

CIRCUIT_STOP_VERBOSE_NAME = _(u'Place')
CIRCUIT_STOP_VERBOSE_NAME_PLURAL = _(u'Places')
CIRCUIT_STOP_CIRCUIT = _(u'Route')
CIRCUIT_STOP_PLACE = _(u'Place')
CIRCUIT_STOP_DESCRIPTION = _(u'Description')
CIRCUIT_STOP_POSITION = _(u'Position')

CIRCUIT_STOP_UNICODE = _(u'Place %(place)s as part of the route %(circuit)s')

VISIT_VERBOSE_NAME = _(u'Visit')
VISIT_VERBOSE_NAME_PLURAL = _(u'Visits')
USER_VISITING = _(u'Visitor')
CIRCUIT_VISITED = _(u'Visited route')
VISIT_DURATION = _(u'Visit duration')

RATING_VERBOSE_NAME = _(u'Route rating')
RATING_VERBOSE_NAME_PLURAL = _(u'Route ratings')
RATING_USER = _(u'Rating user')
RATING_CIRCUIT = _(u'Rated route')
RATING_VOTE = _(u'Rating')

VOTE_TYPE_UPVOTE = _(u'Upvote')
VOTE_TYPE_DOWNVOTE = _(u'Downvote')
VOTE_TYPE_PENDING = _(u'Pending vote')

CCF_VERBOSE_NAME = _(u'Registering interested category')
CCF_VERBOSE_NAME_PLURAL = _(u'Registering interested categories')

CCF_USER = _(u'User')
CCF_CATEGORY = _(u'Category')
CCF_UNICODE = _(
    u'%(user)s is interested in %(category)s'
)

# CIRCUIT CATEGORIES
FOOD_AND_DRINK = _(u'Food & Drink')
FAMILY_AND_KIDS = _(u'Family & Kids')
ARTS_AND_CULTURE = _(u'Arts & Culture')
ARCHITECTURE = _(u'Architecture')
NIGHTLIFE = _(u'Nightlife')
TV_AND_FILM = _(u'TV & Film')
ROMANCE = _(u'Romance')
SPORTS_AND_FITNESS = _(u'Sports & Fitness')
LIFESTYLE = _(u'Lifestyle')
ACADEMIC_AND_EDUCATION = _(u'Academic & Education')
NATURE = _(u'Nature')
TOURISM = _(u'Tourism')
HISTORY = _(u'History')
SHOPPING = _(u'Shopping')
MISC = _(u'Miscellaneous')

# Circuit sources

SOURCE_WORLDRAT_USERS = _(u'Worldrat users')
SOURCE_WORLDRAT_STAFF = _(u'Worldrat staff')
SOURCE_NEXTSTOP = _(u'Nextstop')

# MESSAGES
CIRCUIT_REMIXED_SUCCES = _(u'Remix succesful! You have created a new route from %(route)s')


# API

NON_EXISTANT_CIRCUIT = _(u'No route exists under the given identifier')
NON_EXISTANT_STOP = _(
    u'No place with id %(stop_id)s exists under a route '
    u'with id %(circuit_id)s or the route does not exist.'
)
NON_EXISTANT_STOP_WITH_IDS = _(
    u'No place with id %(place_id)s exists in the '
    u'route with id %(circuit_id)s'
)

NON_EXISTANT_CIRCUIT_CATEGORY = _(
    u'The category does not exist for any routes'
)

NON_EXISTANT_USER = _(u'User does not exist')


UNAUTHORIZED_CIRCUIT_EDIT = _(
    u'Only the author of the route can make changes to it.'
)
PLACE_ALREADY_INCLUDED = _(
    u'The place is already included in the route'
)
CIRCUIT_COLLECTION_NAME = _(u'Route collection')
CIRCUIT_CATEGORY_COLLECTION_NAME = _(u'Route category collection')
UNKNOWN_CATEGORY_VALUE = _(u'Unknown category value')

UNKNOWN_GMAC = _(u'GMAC not known %(gmac)s')

CIRCUIT_ALREADY_PUBLISHED = _(u'Route already published')
CIRCUIT_ALREADY_UNPUBLISHED = _(u'Route already unpublished')

CIRCUIT_ALREADY_UPVOTED = _(u'Route already upvoted by user')
CIRCUIT_ALREADY_DOWNVOTED = _(u'Route already downvoted by user')

CIRCUIT_ALREADY_FAVORITE = _(u'Route already favorited by user')
CIRCUIT_NOT_IN_FAVORITE = _(u'Route has not been favorited by user')
CIRCUIT_AUTHOR_SELF_FAVORITE = _(
    u'A route can not be favorited by its author'
)

CATEGORY_ALREADY_FOLLOWED = _(u'Route category already followed')
CATEGORY_NOT_FOLLOWED = _(u'Route category is not being followed')

# DEFAULTS

CHOOSE_CATEGORY = _(u'Choose category')

DEFAULT_CIRCUIT_NAME = _(u'Untitled route')

