from rest_framework import serializers
from . models import User
from . models import Bucket
from . models import Device
from . models import File
import bcrypt

class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def create(self, validated_data):
        # Encode password string as utf-8, hashing it, then decoding it back to string to store in the database
        validated_data['password'] = bcrypt.hashpw(bytes(validated_data['password'], "utf-8"), bcrypt.gensalt()).decode("utf-8")
        return User.objects.create(**validated_data)

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