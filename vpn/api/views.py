from .serializers import *
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth import login,logout
from rest_framework.permissions import IsAuthenticated,AllowAny
from vpn.models import Server,EmailToken
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from django.utils.crypto import get_random_string
from datetime import datetime,timedelta
from rest_framework import generics
import pytz

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Custom Authentication"""

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening



class SignUpUser(CreateAPIView):
    """This view is used for create token on registration"""

    serializer_class = SignUpSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]

    def post(self,request):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            serializer.save()
            user_data = serializer.data
            user = User.objects.get(username=user_data['username'] ,email=user_data['email'])
            user.is_active = False
            user.save()
            current_site = get_current_site(request).domain
            unique_id = get_random_string(length=400)
            #current_time = datetime.now()
            #future_time = current_time + timedelta(minutes=1)
            create_token= EmailToken.objects.create(user=user,token = unique_id)
            future_time = create_token.created_at + timedelta(minutes=1)
            create_token.expiration_time  = future_time
            create_token.save()
            relativeLink = reverse('email-verify')
            absurl = 'http://'+current_site+relativeLink+create_token.token
            email_body = 'Hi '+user.username + \
                    ' Use the link below to verify your email \n' + absurl
            data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}

            Util.send_email(data)
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class RenewTokenView(APIView):
    """This class is used to regenterate the Token on expiration or some cause"""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]

    def post(self,request):

        data = request.data
        print(data['username'])
        print(data['email'])
        user = User.objects.get(username=data['username'] ,email=data['email'])
        if user.is_active == False:
            current_site = get_current_site(request).domain
            unique_id = get_random_string(length=400)
            current_time = datetime.now()
            future_time = current_time + timedelta(minutes=1)
            get_user = EmailToken.objects.get(user=user)
            get_user.token = unique_id
            get_user.expiration_time = future_time
            get_user.save()
            relativeLink = reverse('email-verify')
            absurl = 'http://'+current_site+relativeLink+get_user.token
            email_body = 'Hi '+user.username + \
                    ' Use the link below to verify your email \n' + absurl
            data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}

            Util.send_email(data)
            return Response('Email Verification Sent', status = status.HTTP_201_CREATED)
        return Response("User is already verified" ,status = status.HTTP_400_BAD_REQUEST)


class VerifyEmail(APIView):
    """This view is used to verify the token sent on email"""

    def get(self, request, token):

        user = EmailToken.objects.get(token = token)

        print(user.user.username)
        utc=pytz.UTC
        if utc.localize(datetime.now()) < user.expiration_time:
            print(user.created_at)
            print(user.expiration_time)
            user.user.is_active = True
            user.user.save()

            return Response('succussfully created the user')
        else:
            user.expired = True
            user.save()
            return Response('Token Expired')


class LoginView(APIView):
    """This is the login api for android app"""

    serializer_class = LoginUserSerializer
    permission_classes = [AllowAny]
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]


    def post(self, request, format=None):

        serializer = self.serializer_class(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        queryset = User.objects.all()
        user = get_object_or_404(queryset, username = request.user)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)




class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            token =get_random_string(length=400)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse('password-reset-complete')

            absurl = 'http://'+current_site + relativeLink + token
            email_body = 'Hello' + user.username +', \n Use link below to reset your password  \n' + \
                absurl
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
        return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request, token):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


class LogOutView(APIView):
    """To logout out of application"""

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        logout(request)

        return Response('User Logged out successfully')



class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'message': 'Password updated successfully',
            }

            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServerView(APIView):
    """To get all the server present"""
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]

    def get(self, request, format=None):
        server = Server.objects.all()
        serializer = ServerSerializer(server, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)


class ServerPostView(CreateAPIView):
    """To create a new server"""

    serializer_class = ServerSerializer
    queryset = Server.objects.all()
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]

    def post(self,request):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class ServerRetrieveView(APIView):
    """Get server by id and perform update and delete request"""
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]

    def get_object(self,request,id):
        try:
            server = Server.objects.get(id=id)
            return server

        except Server.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self,request,id):

        songs = self.get_object(request,id)
        serializer = ServerSerializer(songs)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self,request,id):

        server = self.get_object(request,id)
        serializer = ServerSerializer(server, data=request.data)

        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):

        server = self.get_object(request,id)
        server.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)