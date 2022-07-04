from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForDetail,
)
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params
from utils.paginations import EndlessPagination
from tweets.services import TweetService
from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator


class TweetViewSet(viewsets.GenericViewSet):
    serializer_class = TweetSerializerForCreate
    queryset = Tweet.objects.all()
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            #Can access without logging in
            return [AllowAny()]
        #Need to log in to access
        return [IsAuthenticated()]

    @method_decorator(ratelimit(key = 'user_or_ip', rate = '5/s', method = 'GET', block = True))
    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        return Response(TweetSerializerForDetail(
            tweet,
            context = {'request': request},
        ).data)

    #Match self.action
    @required_params(params = ['user_id'])
    def list(self, request, *args, **kwargs):
        user_id = request.query_params['user_id']
        cached_tweets = TweetService.get_cached_tweets(user_id)
        page = self.paginator.paginate_cached_list(cached_tweets, request)
        if page is None:
            # obtain from db
            queryset = Tweet.objects.filter(user_id = user_id).order_by('-created_at')
            page = self.paginate_queryset(queryset)
        #select * from twitter_tweets
        #where user_id = xxx
        #order by created_at desc
        serializer = TweetSerializer(
            page,
            context = {'request': request},
            many = True,
        ) #return list of dict
        return self.get_paginated_response(serializer.data)


    @method_decorator(ratelimit(key = 'user', rate = '1/s', method = 'POST', block = True))
    @method_decorator(ratelimit(key = 'user', rate = '5/m', method = 'POST', block = True))
    def create(self, request, *args, **kwargs):
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
        return Response(TweetSerializer(
            tweet,
            context = {'request': request}).data,
            status = 201
        )
