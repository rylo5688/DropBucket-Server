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
import bcrypt

# Create your views here.
class userSignUp(APIView):
    def post(self, request):
        # TODO: Need to make this HTTPS so we aren't sending plaintext passwords
        serializer = userSerializer(data=request.data)
        if serializer.is_valid():
            # Check if this User already exists before creating a new entry
            querySet = User.objects.filter(username=request.data['username'])
            if len(querySet) == 0:
                # User doesn't exist, so create an entry
                serializer.save()
                return Response({"message": "User successfully created! You can now sign in."}, status=status.HTTP_201_CREATED)

            # Let the client know that the user already exists by telling them there is a conflict
            return Response({"message": "User already exists."}, status=status.HTTP_409_CONFLICT)

        return Response({"message": "Incorrectly formatted request body."}, status=status.HTTP_400_BAD_REQUEST)

class userSignIn(APIView):
    def post(self, request):
        # TODO: Need this to contain device information so we can add it to the database
        serializer = userSerializer(data=request.data)
        if serializer.is_valid():
            # Look for a matching user and check to see if the correct password was given.
            # TODO: Give them a session key to the client so they don't need to log in each time
            querySet = User.objects.filter(username=request.data['username'])
            if len(querySet) == 0: # User doesn't exist, so return error
                return Response({"message": "User doesn't exist. Please create an account."}, status=status.HTTP_409_CONFLICT)

            # Check if the passwords match
            match = bcrypt.checkpw(bytes(request.data["password"], "utf-8"), bytes(querySet[0].password, "utf-8"))
            if match:
                return Response({"message": "Sign in successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Incorrect password"}, status=status.HTTP_409_CONFLICT)

        return Response({"message": "Incorrectly formatted request body."}, status=status.HTTP_400_BAD_REQUEST)

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
