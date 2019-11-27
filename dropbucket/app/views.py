from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . models import User
from . models import Bucket
from . models import Device
from . models import File
from . serializers import userSerializer
from . serializers import bucketSerializer
from . serializers import deviceSerializer
from . serializers import fileSerializer

# Create your views here.
class userList(APIView):

    def get(self, request):
        user = User.objects.all()
        serializer = userSerializer(user, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = userSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class userDetail(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise get_object_or_404
        
    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = userSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = userSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class bucketList(APIView):
    def get(self, request):
        bucket = Bucket.objects.all()
        serializer = bucketSerializer(bucket, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = bucketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class deviceList(APIView):
    def get(self, request):
        device = Device.objects.all()
        serializer = deviceSerializer(device, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = deviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class fileList(APIView):
    def get(self, request):
        file = File.objects.all()
        serializer = fileSerializer(file, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = fileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
