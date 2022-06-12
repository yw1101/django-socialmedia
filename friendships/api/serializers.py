from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from friendships.services import FriendshipService


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source = 'from_user')
    has_followed = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        #user is actually the from_user
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FriendshipService.has_followed(
            self.context['request'].user,
            obj.from_user
        )


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source = 'to_user')
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        #user is actually the from_user
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FriendshipService.has_followed(
            self.context['request'].user,
            obj.from_user
        )

class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'You cannot follow yourself.',
            })
        if not User.objects.filter(id = attrs['to_user_id']).exists():
            raise ValidationError({
                'message': 'You cannot follow a non-exist user.',
            })
        return attrs

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        return Friendship.objects.create(
            from_user_id = validated_data['from_user_id'],
            to_user_id = validated_data['to_user_id'],
        )
