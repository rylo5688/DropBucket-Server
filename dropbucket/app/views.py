from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib import auth
from django import forms
from . models import User
from . models import Bucket
from . models import Device
from . models import File
from . serializers import userSerializer
from . serializers import bucketSerializer
from . serializers import deviceSerializer
from . serializers import fileWriteSerializer, fileReadSerializer
from . import GCPStorage
from tempfile import TemporaryFile
import bcrypt
import shutil
import os

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
                # Give user session key set to expire in 30 seconds
                u = User.objects.get(username=request.data['username'])
                request.session['user_id'] = u.id
                request.session.set_expiry(86400)
                
                return Response({"message": "Sign in successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Incorrect password"}, status=status.HTTP_409_CONFLICT)

        return Response({"message": "Incorrectly formatted request body."}, status=status.HTTP_400_BAD_REQUEST)

#TODO: logout that deletes session key
# def logout(request):
#     try:
#         del request.session['user_id']
#     except KeyError:
#         pass
#     return HttpResponse("You're logged out.")

class userView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = userSerializer



# could break these out into fileUpload, fileDownload, and fileDelete
class fileList(APIView):

    # POST /file
    # Uploads a file to GCP
    # TODO: Delete file_serializer associated instance/find a way to upload without creating in the first place
    def post(self, request, *args, **kwargs):
        # Django magic with session (?)
        u_id = request.session['user_id']
        
        # Add user_id and relative path to request data  (TODO: change relative path from just using name)
        filename = request.FILES['file'].name
        request.data.update({"user_id": u_id, "relative_path": filename})
        file_serializer = fileWriteSerializer(data=request.data)

        if file_serializer.is_valid(): 
                file_serializer.save()

                # Create or access bucket for user
                g = GCPStorage.GCPStorage(u_id)
                g.upload(file_serializer.save())

                # Delete db entry and local copy
                File.objects.all().delete()
                os.remove(filename)

                return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
                return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET /file
    def get(self, request, *args, **kwargs):
        # Django magic with session (?)
        u_id = request.session['user_id']

        # Append user_id to file
        request.data.update({"user_id": u_id})
        file_serializer = fileReadSerializer(data=request.data)

        if file_serializer.is_valid(): 
                file_serializer.save()

                # Create or access bucket for user
                g = GCPStorage.GCPStorage(u_id)
                g.download(file_serializer.save())

                # Delete db entry
                File.objects.all().delete()

                return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
                return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /file
    def delete(self, request, *args, **kwargs):
        # Django magic with session (?)
        u_id = request.session['user_id']

        # Add user_id and relative path to request data  (TODO: change relative path from just using name)
        filename = request.FILES['file'].name
        request.data.update({"user_id": u_id, "relative_path": filename})
        file_serializer = fileWriteSerializer(data=request.data)

        if file_serializer.is_valid(): 
                file_serializer.save()

                # Create or access bucket for user
                g = GCPStorage.GCPStorage(u_id)
                g.delete(file_serializer.save())

                # Delete db entry and local copy
                File.objects.all().delete()
                os.remove(filename)

                return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
                return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

