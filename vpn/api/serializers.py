from genericpath import exists
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from vpn.models import Server,Membership
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

class SignUpSerializer(serializers.ModelSerializer):
    """This serializer is used to register the user or signup the user"""

    password = serializers.CharField(write_only = True,required=True,validators=[validate_password])
    password2 = serializers.CharField(write_only = True,required=True,)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password2',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username = self.validated_data['username'],
            email = self.validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class MembershipSerializer(serializers.ModelSerializer):
    """This Serializer shows the membership of persons
    against user that is being handled in User Serializer"""

    class Meta:
        model = Membership
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """This serializer is used to get user and its details"""
    membership = MembershipSerializer(read_only = True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'membership']


class LoginUserSerializer(serializers.ModelSerializer):
    """
    This serializer defines two fields for authentication:
      * username
      * password.
    It will try to authenticate the user with when validated.
    """
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    class Meta:
        model = User
        fields = '__all__'

    def validate(self, attrs):
        # Take username and password from request
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Try to authenticate the user using Django auth framework.
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                # If we don't have a regular user, raise a ValidationError
                msg = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        # We have a valid user, put it in the serializer's validated_data.
        # It will be used in the view.
        attrs['user'] = user
        return attrs


class ServerSerializer(serializers.ModelSerializer):
    """This serializer is used for server model"""

    class Meta:
        model = Server
        fields = "__all__"


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2) 

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)

    class Meta:
        fields = ['password']

    def validate(self, attrs):
        try:
            username = attrs.get('username')
            password = attrs.get('password')
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)
