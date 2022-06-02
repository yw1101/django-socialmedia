from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import exceptions
from accounts.models import UserProfile 


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserSerializerWithProfile(UserSerializer):
    nickname = serializers.CharField(source = 'profile.nickname')
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None

    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'avatar_url')

class UserSerializerForTweet(UserSerializerWithProfile):
    class Meta:
        model = User
        fields = ('id', 'username')


class UserSerializerForLike(UserSerializerWithProfile):
    pass


class UserSerializerForComment(UserSerializerWithProfile):
    pass


class UserSerializerForFriendship(UserSerializerWithProfile):
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

class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields =('nickname', 'avatar')
