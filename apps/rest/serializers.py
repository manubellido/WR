# -*- coding: utf-8 -*-

import datetime
import decimal
from rfc3339 import rfc3339
from django.utils import datetime_safe
from django.utils.simplejson import JSONEncoder


class RESTfulJSONEncoder(JSONEncoder):                                
    """                                                                         
    JSONEncoder subclass that knows how to encode decimal types and also
    date/time using the RFC 3339 format and.  
    """                                                                         
                                                                                
    DATE_FORMAT = "%Y-%m-%d"                                                    
    TIME_FORMAT = "%H:%M:%S"                                                    
                                                                                
    def default(self, o):                                                       
        if isinstance(o, datetime.datetime):                                    
            d = datetime_safe.new_datetime(o)                                   
            return rfc3339(d)
        elif isinstance(o, datetime.date):                                      
            d = datetime_safe.new_date(o)                                       
            return d.strftime(self.DATE_FORMAT)                                 
        elif isinstance(o, datetime.time):                                      
            return o.strftime(self.TIME_FORMAT)                                 
        elif isinstance(o, decimal.Decimal):                                    
            return str(o)                                                       
        else:                                                                   
            return super(RESTfulJSONEncoder, self).default(o)
