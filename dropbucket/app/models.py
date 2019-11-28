from django.db import models

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
    filename = models.CharField(max_length=255)
    path = models.CharField(max_length=4096)
    gcp_URL = models.CharField(max_length=2000)
    md5 = models.CharField(max_length=32)



