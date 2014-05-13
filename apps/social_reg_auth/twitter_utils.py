
import json
import requests

def get_profile_dict(screen_name):
    """ Returns a dict object containing all the information
    of a user, requesting it on Twitter resource: 
    https://api.twitter.com/1.1/users/show.json """

    url = 'https://api.twitter.com/1/users/show.json?screen_name=%s' % (
        screen_name.lower()
    )

    # make the request to url
    req = requests.get(url)
    # get the content of the response
    content = req.content
    # cast it to a JSON object dict-like
    json_obj = json.loads(content)

    return json_obj

