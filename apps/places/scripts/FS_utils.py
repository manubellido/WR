# -*- coding: utf-8 -*-
import foursquare
try:
    import json
except ImportError:
    import simplejson as json
    
from django.conf import settings
from places import settings as place_settings


def get_FS_categories(save=True):
    """
    gets the categories from 4SQR API, if save is True, then save file 
    to /static/foursquare/categories.json, otherwise return JSON
    """
    client = foursquare.Foursquare(
        client_id=settings.FS_CLIENT_ID, 
        client_secret=settings.FS_CLIENT_SECRET,
        version=place_settings.FS_API_VERSION
    )

    response = client.venues.categories()

    if save:
        FILE = open(settings.FS_CATEGORIES_FILE,"w")
        FILE.writelines(json.dumps(response, indent=4))
    else:
        return json.dumps(response, indent=4)
 
    
def venue_cat_parser():
    """
    parses the categories of venues from JSON and return a 
    list o lists with categories
    """
    results = get_FS_categories(save=False)
    results = json.loads(results)
    
    all_cats = []
    for cat in results['categories']:
        # parent_id, id, name, pluralName, shortName, 
        # icon: prefix, sizes, name(image_format);         
        row = (
            None,
            cat['id'], 
            cat['name'], 
            cat['pluralName'],
            cat['shortName'],
            cat['icon']['prefix'],
            #cat['icon'][0:-6],
            #cat['icon']['sizes'],
            '32',
            cat['icon']['suffix'],
            #cat['icon'][-4:-1],
        )
        all_cats.append(row)
        for sub_cat in cat['categories']:
            # parent_id, id, name, pluralName, shortName, 
            # icon: prefix, sizes, name(image_format);
            row = (
                cat['id'],
                sub_cat['id'], 
                sub_cat['name'], 
                sub_cat['pluralName'],
                sub_cat['shortName'],
                sub_cat['icon']['prefix'],
                #sub_cat['icon'][0:-4],
                #cat['icon']['sizes'],
                '32',
                sub_cat['icon']['suffix'],
                #sub_cat['icon'][-4:-1],
            )
            all_cats.append(row)
            for leaf_cat in sub_cat['categories']:
                # parent_id, id, name, pluralName, shortName, 
                # icon: prefix, sizes, name(image_format);
                row = (
                    sub_cat['id'],
                    leaf_cat['id'], 
                    leaf_cat['name'], 
                    leaf_cat['pluralName'],
                    leaf_cat['shortName'],
                    leaf_cat['icon']['prefix'],
                    #leaf_cat['icon'][0:-4],
                    #cat['icon']['sizes'],
                    '32',
                    leaf_cat['icon']['suffix'],
                    #leaf_cat['icon'][-4:-1],
                )
                all_cats.append(row)   
                                              
    return  all_cats

