from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer
from utils.paginations import EndlessPagination
from newsfeeds.services import NewsFeedService
from newsfeeds.models import NewsFeed


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = EndlessPagination

    def get_queryset(self):
        # Customize queryset，because viewing newsfeed needs authencation
        # user = newsfeed of user logging in now
        # or can be self.request.user.newsfeed_set.all()
        return NewsFeed.objects.filter(user = self.request.user)

    def list(self, request):
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(request.user.id)
        page = self.paginator.paginate_cached_list(cached_newsfeeds, request)
        if page is None:
            #get from database
            queryset = NewsFeed.objects.filter(user = request.user)
            page = self.paginate_queryset(queryset)
        serializer = NewsFeedSerializer(
            page,
            context = {'request': request},
            many = True,
        )
        return self.get_paginated_response(serializer.data)
