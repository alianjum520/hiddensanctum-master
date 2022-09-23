from .serializers import *
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from django.contrib.auth import login,logout
from rest_framework.permissions import IsAuthenticated,AllowAny
from vpn.models import Server

class UserData(APIView):

    def get(self, request, format=None):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)


class SignUpUser(CreateAPIView):

    serializer_class = SignUpSerializer
    queryset = User.objects.all()

    def post(self,request):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class LoginView(CreateAPIView):

    serializer_class = LoginUserSerializer
    permission_classes = [AllowAny]

    def post(self, request, format=None):

        serializer = self.serializer_class(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)


class LogOutView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        logout(request)

        return Response('User Logged out successfully')


class ServerView(APIView):

    def get(self, request, format=None):
        server = Server.objects.all()
        serializer = ServerSerializer(server, many=True)
        return Response(serializer.data, status = status.HTTP_200_OK)

class ServerPostView(CreateAPIView):

    serializer_class = ServerSerializer
    queryset = Server.objects.all()

    def post(self,request):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)

        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)