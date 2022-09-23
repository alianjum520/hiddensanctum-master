from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    """This serializer is used to get user and its details"""

    class Meta:
        model = User
        fields = '__all__'


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


'''class loginUserSerializer(serializers.ModelSerializer):
    """
    This serializer defines two fields for authentication:
      * username
      * password.
    It will try to authenticate the user with when validated.
    """

    class Meta:
        model = User
        fields = ['username', '']'''