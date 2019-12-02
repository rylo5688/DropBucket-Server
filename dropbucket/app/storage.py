from django.db import models
from django.core.files.storage import FileSystemStorage

class FileStorage(FileSystemStorage):
        # In FileSystemStorage, this function replaces spaces with underscores. 
        # Overriding to allow file names with spaces in them.
        def get_valid_name(self, name):
            return name