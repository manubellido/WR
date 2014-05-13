import os

from django.core.files.storage import FileSystemStorage as BaseFileSystemStorage
from django.conf import settings
from django.core.files import locks
from django.core.files.move import file_move_safe

class FileSystemStorage(BaseFileSystemStorage):
    """
    Standard filesystem storage
    """
    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        # NOP
        return name

    def _save(self, name, content):
        full_path = self.path(name)
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        elif not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)
        # This file has a file path that we can move.
        if hasattr(content, 'temporary_file_path'):
            file_move_safe(content.temporary_file_path(), full_path)
            content.close()
        # This is a normal uploadedfile that we can stream.
        else:
            # This fun binary flag incantation makes os.open throw an
            # OSError if the file already exists before we open it.
            fd = os.open(full_path, os.O_WRONLY | os.O_TRUNC \
                    | os.O_CREAT | getattr(os, 'O_BINARY', 0))
            try:
                locks.lock(fd, locks.LOCK_EX)
                for chunk in content.chunks():
                    os.write(fd, chunk)
            finally:
                locks.unlock(fd)
                os.close(fd)
        if settings.FILE_UPLOAD_PERMISSIONS is not None:
            os.chmod(full_path, settings.FILE_UPLOAD_PERMISSIONS)
        return name
