from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib import auth
from django.utils.encoding import smart_str
from . models import User, Bucket, Device, File
from . serializers import userSerializer, bucketSerializer, deviceSerializer, fileSerializer
from . import GCPStorage
from . import TCPSockets
import bcrypt
import os
import io

# Handles user sign up, adds entry to DB 
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

# Handles user sign in and associates a session with a given device
class userSignIn(APIView):
    def post(self, request):
        # TODO: Need this to contain device information so we can add it to the database
        user_serializer = userSerializer(data=request.data)

        if user_serializer.is_valid():
            # Look for a matching user and check to see if the correct password was given.
            # TODO: Give them a session key to the client so they don't need to log in each time
            querySet = User.objects.filter(username=request.data['username'])
            if len(querySet) == 0: # User doesn't exist, so return error
                return Response({"message": "User doesn't exist. Please create an account."}, status=status.HTTP_409_CONFLICT)

            # Check if the passwords match
            match = bcrypt.checkpw(bytes(request.data["password"], "utf-8"), bytes(querySet[0].password, "utf-8"))
            if match:
                u = User.objects.get(username=request.data['username'])

                # Update device table
                device_id = request.data['device_id']
                device_serializer = deviceSerializer(data={"user_id": u.id, "device_id": device_id, "sync": "true"})

                if device_serializer.is_valid():
                    try:
                        obj = Device.objects.get(device_id=device_id)
                    except Device.DoesNotExist:
                        device_serializer.save()
                else:
                    print(device_serializer.errors)
                    return Response({"message": "Incorrectly formatted request body."}, status=status.HTTP_400_BAD_REQUEST)

                # Give user session key set to expire in 1 day
                request.session['device_id'] = device_id
                request.session.set_expiry(86400)

                # Get bucket info
                g = GCPStorage.GCPStorage(u.pk)
                bucketInfo = g.list()

                return Response({ **bucketInfo, **{"message": "Sign in successful"} }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Incorrect password"}, status=status.HTTP_409_CONFLICT)

        return Response({"message": "Incorrectly formatted request body."}, status=status.HTTP_400_BAD_REQUEST)

#TODO: logout that deletes session key
# def logout(request):
#     try:
#         del request.session['user_id']
#     except KeyError:d
#         pass
#     return HttpResponse("You're logged out.")

# Default GET, POST, and DELETE methods for User
class userView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = userSerializer

# Default GET, POST, and DELETE methods for Bucket
class bucketView(viewsets.ModelViewSet):
    queryset =Bucket.objects.all()
    serializer_class = bucketSerializer

# Default GET, POST, and DELETE methods for Device
class deviceView(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = deviceSerializer


# GET, POST, and DELETE methods for files
class fileDetail(APIView):

    # POST /file
    # Uploads a file to GCP
    def post(self, request, *args, **kwargs):

        # Django magic for session associated with a device
        device_id = request.session['device_id']

        # Append user id to request data
        device = Device.objects.get(device_id=device_id)
        u_id = device.user_id.pk
        filename = request.FILES['file'].name
        request.data.update({"user_id": u_id, "relative_path": filename})
        file_serializer = fileSerializer(data=request.data)

        if file_serializer.is_valid():

            # Create or access bucket for user
            g = GCPStorage.GCPStorage(u_id)

            # Copy request file to tempfile
            f = request.FILES['file']
            with open(filename, 'wb+') as tmp:
                for chunk in f.chunks():
                    tmp.write(chunk)

                tmp.close()
                # Create or access bucket for user and upload from temp file
                g = GCPStorage.GCPStorage(u_id)

                g.upload(filename)

            # Delete temp file
            os.remove(filename)


            # Send sync requests to n-1 connected devices
            bucketInfo = g.list()
            sockets = TCPSockets.TCPSockets()
            sockets.sendSyncRequests(User.objects.get(id=u_id).username, device_id, bucketInfo)

            return Response({"message": "File successfully uploaded"}, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # https://stackoverflow.com/questions/1156246/having-django-serve-downloadable-files
    # GET /file
    def get(self, request, *args, **kwargs):
        # Django magic for session associated with a device
        device_id = request.session['device_id']

        # Append user_id and relative path to request data to be serialized
        relative_path = request.GET.get('relative_path')
        device = Device.objects.get(device_id=device_id)
        u_id = device.user_id.pk
        request.data.update({"user_id": u_id, "relative_path": relative_path})
        file_serializer = fileSerializer(data=request.data)

        if file_serializer.is_valid():

            # Create or access bucket for user and download file
            g = GCPStorage.GCPStorage(u_id)
            tempfile_path = g.download(relative_path, device_id)

            if os.path.exists(tempfile_path):
                # with open(tempfile_path, 'r', encoding='utf-8', errors='ignore') as tempfile:
                #     read_bytes = tempfile.read()
                with open(tempfile_path, 'rb') as tempfile:
                    response = HttpResponse(tempfile.read(), content_type="application/force-download")
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(tempfile_path)
                    response['X-Sendfile'] = smart_str(tempfile_path)

            # Delete temp file
            os.remove(tempfile_path)

            return response
            # return Response({"data": read_bytes}, status=status.HTTP_200_OK)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # DELETE /file
    def delete(self, request, *args, **kwargs):
        # Django magic for session associated with a device
        device_id = request.session['device_id']

        # Append user_id and relative path to request data to be serialized
        relative_path = request.GET.get('relative_path')
        device = Device.objects.get(device_id=device_id)
        u_id = device.user_id.pk

        file_data = {"user_id": u_id, "relative_path": relative_path}
        file_serializer = fileSerializer(data=file_data)

        if file_serializer.is_valid():

            # Create or access bucket for user and delete file
            g = GCPStorage.GCPStorage(u_id)
            g.delete(relative_path)

            # Send sync requests to n-1 connected devices
            bucketInfo = g.list()
            sockets = TCPSockets.TCPSockets()
            sockets.sendSyncRequests(User.objects.get(id=u_id).username, device_id, bucketInfo)

            return Response({"message": "File successfully deleted"}, status=status.HTTP_200_OK)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('messages')