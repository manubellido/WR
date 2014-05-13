# -*- coding: utf-8 -*-

import urllib
import base64

from django.core.validators import validate_email

from user_profile import settings as accounts_settings


def psv_get(request, var_name, default_value):
   if var_name in request.session[accounts_settings.PSV_DICT_NAME]:
        return request.session[accounts_settings.PSV_DICT_NAME][var_name]
   else:
        return default_value

def psv_set(request, var_name, value):
    if accounts_settings.PSV_DICT_NAME in request.session:
        pass
    else:
        request.session[accounts_settings.PSV_DICT_NAME]={}
 
    request.session[accounts_settings.PSV_DICT_NAME][var_name] = value
    return value

def retrieve_image(url):
    socket= urllib.urlopen(url)
    contents = socket.read()
    socket.close()
    return contents
   
def retrieve_image_as_base_64(url):
    
    contents=retrieve_image(url) 
    return base64.b64encode(contents)

def psv_exists(request, var_name):
    if accounts_settings.PSV_DICT_NAME in request.session:
        return var_name in request.session[accounts_settings.PSV_DICT_NAME]
    else:
        return False


def psv_save(request):
    if accounts_settings.PSV_DICT_NAME in request.session:
        return request.session[accounts_settings.PSV_DICT_NAME]

    else:
        return {}

def psv_restore(request, new_dict):
    request.session[accounts_settings.PSV_DICT_NAME] = new_dict
