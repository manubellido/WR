# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _


# Topics model strings
TOPIC_VERBOSE_NAME = _(u'Topic')
TOPIC_VERBOSE_NAME_PLURAL = _(u'Topics')
TOPIC_NAME = _(u'Topic name')
TOPIC_SLUG = _(u'Slug')
TOPIC_PARENT_TOPIC = _(u'Elder Topic')
TOPIC_FOLLOWERS = _(u'Followers')
TOPIC_INTERESTED_USERS = _(u'Following users')

# Follow model strings
TOPIC_FOLLOW_VERBOSE_NAME = _(u'Topic Follow')
TOPIC_FOLLOW_VERBOSE_NAME_PLURAL = _(u'Topic Follows')
TOPIC_FOLLOW_USER = _(u'Follower')
TOPIC_FOLLOW_TOPIC = _(u'Topic')
TOPIC_FOLLOW_CREATED_AT = _(u'Created at')
TOPIC_FOLLOW_UNICODE = _(
    u'User %(user)s follows topic %(topic)s'
)

# TopicInterest model strings
TOPIC_INTEREST_VERBOSE_NAME = _(u'Interest topic')
TOPIC_INTEREST_VERBOSE_NAME_PLURAL = _(u'Interesting topics')

TOPIC_INTEREST_USER = _(u'Interested user')
TOPIC_INTEREST_TOPIC = _(u'Interested users')
TOPIC_INTEREST_CREATED_AT = _(u'Created at')
TOPIC_INTEREST_UNICODE = _(
    u'User %(user)s is interested in topic %(topic)s'
)
