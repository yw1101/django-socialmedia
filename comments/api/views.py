from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from utils.permissions import IsObjectOwner
from utils.decorators import required_params
from inbox.services import NotificationService
from ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator


class CommentViewSet(viewsets.GenericViewSet):
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params = ['tweet_id'])
    @method_decorator(ratelimit(key = 'user', rate = '10/s', method = 'GET', block = True))
    def list(self, request, *args, **kwargs):
        #id is in the url
        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset).order_by('created_at')
        serializer = CommentSerializer(
        comments,
        context = {'request': request},
        many = True
    )
        return Response(
            {'comments': serializer.data},
            status = status.HTTP_200_OK,
        )
        #make sure to return the hash map

    @method_decorator(ratelimit(key = 'user', rate = '10/s', method = 'POST', block = True))
    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        serializer = CommentSerializerForCreate(data = data)

        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status = status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()
        NotificationService.send_comment_notification(comment)
        return Response(
            CommentSerializer(comment, context = {'request': request},).data,
            status = status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        serializer = CommentSerializerForUpdate(
            instance = comment,
            data = request.data,
        )
        if not serializer.is_valid():
            raise Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status = status.HTTP_400_BAD_REQUEST)
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context = {'request': request},).data,
            status = status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        return Response({'success': True}, status = status.HTTP_200_OK)
