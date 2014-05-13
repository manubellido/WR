# -*- coding: utf-8 -*-

from ordereddict import OrderedDict
from django.contrib.gis.db import models
from django_extensions.db.fields import AutoSlugField
from django.template.defaultfilters import slugify
from django.conf import settings
from django.core.urlresolvers import reverse
from common.utils.strings import multiple_whitespace_to_single_space
from common.models import AuditableModel
from topics import strings
from django.contrib.auth.models import User


class Topic(AuditableModel):
    """
    Topic base class. 'Nuff said.
    """

    name = models.CharField(
        verbose_name=strings.TOPIC_NAME,
        max_length=200,
        unique=True
    )

    slug = AutoSlugField(
        verbose_name=strings.TOPIC_SLUG, 
        populate_from='name', 
        unique=True, 
        editable=False
    )

    # Relationship with Topic as a tree o topics
    parent = models.ManyToManyField("self",
        verbose_name=strings.TOPIC_PARENT_TOPIC,
        related_name='subtopics',
        null=True,
        blank=True
    )

    # Relationship with User through Follow
    followers = models.ManyToManyField(User,
        verbose_name=strings.TOPIC_FOLLOWERS,
        through='TopicFollow',
        related_name='followed_topics'
    )

    # Relationship with User through Interest
    interested_users = models.ManyToManyField(User,
        verbose_name=strings.TOPIC_INTERESTED_USERS,
        through='TopicInterest',
        related_name='topics_of_interest'
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = strings.TOPIC_VERBOSE_NAME
        verbose_name_plural = strings.TOPIC_VERBOSE_NAME_PLURAL

    @staticmethod
    def get_by_name(name):
        try:
            slug = slugify(name)
            return Topic.objects.get(slug=slug)
        except Topic.DoesNotExist:
            return None

    @staticmethod
    def fix_name(name):
        return multiple_whitespace_to_single_space(name).strip()

    @staticmethod
    def exists(name):
        name = Topic.fix_name(name)
        return Topic.get_by_name(name) is not None

    @staticmethod
    def create(name):
        name = Topic.fix_name(name)
        topic = Topic(name=name)
        topic.save()
        return topic

    @staticmethod
    def get_or_create(name):
        name = Topic.fix_name(name)
        if not Topic.exists(name):
            return Topic.create(name)
        else:
            return Topic.get_by_name(name)

    @staticmethod
    def parse_names(names):
        """
        Returns a list of topics
        """
        result = []
        parts = names.split(',')

        trimmed = []
        for elem in parts:
            t_elem = elem.strip()
            if t_elem != '':
                trimmed.append(t_elem)

        for n in trimmed:
            n = Topic.fix_name(n)
            if n not in result:
                result.append(n)
        return result

    def get_absolute_url(self):
        #FIXME: Implementation pending
        return ''

    def get_restful_url(self):
        #FIXME: Use the real URL via reverse from the URLconf settings later
        return "%s%s" % (
            settings.API_V1_PREFIX.rstrip('/'),
            "topics/%s/" % self.slug
        )

    def get_restful_link_metadata(self):
        metadata = OrderedDict()
        metadata['href'] = self.get_restful_url()
        metadata['rel'] = 'alternate'
        metadata['title'] = self.name
        metadata['type'] = 'application/json'
        return metadata


class TopicFollow(models.Model):
    """
    Relation between user and topic where user is following a given topic
    """
    # Relationship with User
    user = models.ForeignKey(User,
        verbose_name=strings.TOPIC_FOLLOW_USER
    )

    # Relationship with Topic
    topic = models.ForeignKey(Topic,
        verbose_name=strings.TOPIC_FOLLOW_TOPIC
    )

    created_at = models.DateTimeField(
        verbose_name=strings.TOPIC_FOLLOW_CREATED_AT,
        auto_now_add=True
    )

    def __unicode__(self):
        return strings.TOPIC_FOLLOW_UNICODE % (self.user, self.topic)

    class Meta:
        verbose_name = strings.TOPIC_FOLLOW_VERBOSE_NAME
        verbose_name_plural = strings.TOPIC_FOLLOW_VERBOSE_NAME_PLURAL


class TopicInterest(models.Model):
    """
    Relation between user and Topic explicitly indicated by user as 
    interenting topic
    """

    # Relationship with User
    user = models.ForeignKey(User,
        verbose_name=strings.TOPIC_INTEREST_USER
    )

    # Relationship with Topic
    topic = models.ForeignKey(Topic,
        verbose_name=strings.TOPIC_INTEREST_TOPIC
    )

    created_at = models.DateTimeField(
        verbose_name=strings.TOPIC_INTEREST_CREATED_AT,
        auto_now_add=True
    )

    def __unicode__(self):
        return strings.TOPIC_INTEREST_UNICODE % (self.user, self.topic)

    class Meta:
        verbose_name = strings.TOPIC_INTEREST_VERBOSE_NAME
        verbose_name_plural = strings.TOPIC_INTEREST_VERBOSE_NAME_PLURAL
    
