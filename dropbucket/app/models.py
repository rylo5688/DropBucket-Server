from django.db import models

# Create your models here.
class users(models.Model):
    access_token=models.CharField(max_length=255)
    refresh_token=models.CharField(max_length=255)
    #expiration=models.IntegerField() -- it's included in response but we don't necessarily need it

    bucket_name=models.CharField(max_length=255, blank=True)