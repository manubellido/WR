import os
import uuid

def uuid_based_picture_name(path):

    def func(instance, filename):
        basename, extension = os.path.splitext(filename)
        basename = str(uuid.uuid4()).replace('-', '')
        extension = extension.lower()
        if extension:
            filename = ''.join([basename, extension])
        else:
            filename = basename
        return os.path.join(path, filename)

    return func
