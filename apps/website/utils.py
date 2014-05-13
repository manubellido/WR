# -*- coding: utf-8 -*-

"""
Utils in website app
"""

from django.core.urlresolvers import reverse
from circuits.constants import CIRCUIT_CATEGORY_CHOICES 
from website.constants import WEBSITE_HOME_SECTION_KEY
from website.constants import WEBSITE_RECOMMENDED_SECTION_KEY
from website import strings


def validate_section(section=None):
    categories = [k.lower() for k in CIRCUIT_CATEGORY_CHOICES.keys()]
    home = WEBSITE_HOME_SECTION_KEY
    if section is None:
        return False
    elif section in categories:
        return True
    elif section == home:
        return True
    else:
        return False


def create_title(gmac, section):
    section_name = CIRCUIT_CATEGORY_CHOICES.get_string(section.upper())
    if section_name == None:
        section_name = strings.GENERIC_SECTION_NAME
    return strings.LOCAL_CIRCUITS_TITLE % {
        'location_name' : gmac.formatted_name,
        'section_name': section_name
    }


def create_url(gmac, section):
    categories = [k.lower() for k in CIRCUIT_CATEGORY_CHOICES.keys()]
    home = WEBSITE_HOME_SECTION_KEY
    recommended = WEBSITE_RECOMMENDED_SECTION_KEY
    if section == home:
        return reverse(
            'home_loc', 
            kwargs={'gmac_slug':gmac.slug}
        )
    elif section == recommended:
        return reverse(
            'recommended_circuits', 
            kwargs={'gmac_slug':gmac.slug}
        )
    elif section in categories:
        return reverse(
            'circuit_category_listing_loc', 
            kwargs={'category_slug':section, 'gmac_slug':gmac.slug}
        )
    else:
        return None       
