from django.contrib import admin
from . models import User
from . models import Bucket
from . models import Device
from . models import File

# Register your models here.
admin.site.register(User)
admin.site.register(Bucket)
admin.site.register(Device)
admin.site.register(File)