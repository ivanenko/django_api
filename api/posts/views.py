import datetime
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from posts.models import Post, Like
from posts.serializers import PostSerializer, UserSerializer
from django.utils import timezone
from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail=True)
    def like(self, request, *args, **kwargs):
        post = self.get_object()
        try:
            Like.objects.get(post_id=post.id, user_id=request.user.id)
            return Response({'message': 'User {} already liked the post {}'.format(request.user.id, post.id)},
                            status=HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            like = Like(post_id=post.id, user_id=request.user.id, date=timezone.now())
            like.save()
            return Response({'message': 'Post {} was liked by user {}'.format(post.id, request.user.id)})

    @action(detail=True)
    def removelike(self, request, *args, **kwargs):
        post = self.get_object()
        try:
            like = Like.objects.get(post_id=post.id, user_id=request.user.id)
            like.delete()
            return Response({'message': 'User {} disliked the post {}'.format(post.id, request.user.id)})
        except ObjectDoesNotExist:
            return Response({'message': 'Post {} was not liked by user {}'.format(post.id, request.user.id)},
                            status=HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def analytics(request):

    if 'date_from' not in request.query_params and 'date_to' not in request.query_params:
        return Response({'error': 'Missing date_from and date_to parameters'}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    date_from = request.query_params['date_from']
    date_to = request.query_params['date_to']

    try:
        date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d')
        date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d')

        likes = Like.objects.filter(date__gte=date_from_obj.date(),
                                    date__lte=date_to_obj.date())

        return Response({
            'likes': likes.count(),
            'date_from': date_from,
            'date_to': date_to
        })
    except Exception:
        return Response({'message': 'Error, check date format'}, status=HTTP_500_INTERNAL_SERVER_ERROR)




