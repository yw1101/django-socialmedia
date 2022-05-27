from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializer

#ModelSerializer: just clarify the fields
class TweetSerializer(serializers.ModelSerializer):
    #Dict in dict to access more info of the users
    user = UserSerializerForTweet()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')


class TweetSerializerWithComments(TweetSerializer):
    comments = CommentSerializer(source = 'comment_set', many = True)

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content', 'comments')



class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length = 6, max_length = 140)

    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user = user, content = content)
        return tweet
