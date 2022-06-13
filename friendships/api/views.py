from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import(
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User
from friendships.api.paginations import FriendshipPagination


class FriendshipViewSet(viewsets.GenericViewSet):
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()
    pagination_class = FriendshipPagination

    @action(methods = ['GET'], detail = True, permission_classes = [AllowAny])
    def followers(self, request, pk):
        #GET /api/friendships/1/followers/
        friendships = Friendship.objects.filter(to_user_id = pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowerSerializer(
            page,
            many = True,
            context = {'request': request}
        )
        return self.get_paginated_response(serializer.data)


    @action(methods = ['GET'], detail = True, permission_classes = [AllowAny])
    def followings(self, request, pk):
        #GET /api/friendships/1/followers/
        friendships = Friendship.objects.filter(from_user_id = pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(
            page,
            many = True,
            context = {'request': request}
        )
        return self.get_paginated_response(serializer.data)


    @action(methods = ['POST'], detail = True, permission_classes = [IsAuthenticated])
    def follow(self, request, pk):
        self.get_object()

        # /api/friendships/<pk>/follow/
        serializer = FriendshipSerializerForCreate(data = {
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status = status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            FollowingSerializer(instance, context = {'request': request}).data,
            status = status.HTTP_201_CREATED,
        )


    @action(methods = ['POST'], detail = True, permission_classes = [IsAuthenticated])
    def unfollow(self, request, pk):
        unfollow_user = self.get_object()
        if request.user.id == unfollow_user.id:
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself.',
            }, status = status.HTTP_400_BAD_REQUEST)

        deleted, _ = Friendship.objects.filter(
            from_user = request.user,
            to_user = unfollow_user,
        ).delete()
        return Response({'success': True, 'deleted': deleted})

    def list(self, request):
        return Response({'message': 'this is Friendship home page'})
