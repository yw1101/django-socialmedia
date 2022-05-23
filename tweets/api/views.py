from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService

class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        if self.action == 'list':
            #Can access without logging in
            return [AllowAny()]
        #Need to log in to access
        return [IsAuthenticated()]

    #Match self.action
    def list(self, request):
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status = 400)

        #select * from twitter_tweets
        #where user_id = xxx
        #order by created_at desc
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id = user_id).order_by('-created_at')
        #tweets is the query set transfered
        serializer = TweetSerializer(tweets, many = True) #return list of dict
        return Response({'tweets': serializer.data})

    def create(self, request):
        serializer = TweetSerializerForCreate(
            data = request.data,
            context = {'request': request},
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status = 400)
            #save will call create method in TweetSerializerForCreate
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status = 201)
