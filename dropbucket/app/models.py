from django.db import models
from . storage import FileStorage

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

class Bucket(models.Model):
    user_id = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE)
    total_space = models.DecimalField(max_digits=9, decimal_places=5)
    gcp_URL = models.CharField(max_length=2000)

class Device(models.Model):
    user_id = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE)
    sync = models.BooleanField()

class File(models.Model):
    user_id = models.ForeignKey(User, to_field='id', on_delete=models.CASCADE)
    file = models.FileField(blank=False, storage=FileStorage())
    relative_path = models.CharField(max_length=4096)