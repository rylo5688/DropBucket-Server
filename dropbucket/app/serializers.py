from rest_framework import serializers
from . models import User
from . models import Bucket
from . models import Device
from . models import File

class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'access_token', 'refresh_token']

class bucketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bucket
        fields = ['id','user_id', 'total_space', 'gcp_URL']

class deviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id','user_id', 'sync']

class fileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id','user_id', 'filename', 'path', 'gcp_URL', 'md5']