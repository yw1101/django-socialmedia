from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserSerializerForTweet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class UserSerializerForLike(UserSerializerForTweet):
    pass


class UserSerializerForComment(UserSerializerForTweet):
    pass

class UserSerializerForFriendship(UserSerializerForTweet):
    pass


class LoginSerializer(serializers.Serializer):
    #help to check whether there are username and password or not
    username = serializers.CharField()
    password = serializers.CharField()


class SignupSerializer(serializers.ModelSerializer):
    #help to check whether there are username and password or not
    username = serializers.CharField(max_length = 20, min_length = 6)
    password = serializers.CharField(max_length = 20, min_length = 6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email','password')

    #will be called when is_valid is called
    def validate(self, data):
        if User.objects.filter(username = data['username'].lower()).exists():
            raise exceptions.ValidationError({
            'message': 'This username has been occupied.'
            })
        if User.objects.filter(email = data['email'].lower()).exists():
            raise exceptions.ValidationError({
            'message': 'This email address has been occupied.'
            })
        return data

    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']
        user = User.objects.create_user(
            username = username,
            email = email,
            password = password,
        )
        user.profile 
        return user
