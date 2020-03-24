from pyhunter import PyHunter
from posts.models import Post
from rest_framework import serializers
from django.contrib.auth.models import User
from threading import Thread
from django.conf import settings


def check_email_function(user_id):
    user = User.objects.get(pk=user_id)
    hunter = PyHunter(settings.PYHUNTER_TOKEN)
    res = hunter.email_verifier(user.email)
    # check result parameters here
    if res['score'] > 10:
        user.is_active = True
        user.save()


class UserSerializer(serializers.HyperlinkedModelSerializer):

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            is_active=False
        )
        user.set_password(validated_data['password'])
        user.save()

        thread = Thread(target=check_email_function, args=(user.id, ))
        thread.start()

        return user

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff', 'password']


class PostSerializer(serializers.HyperlinkedModelSerializer):

    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'text', 'deleted', 'pub_date', 'user_id', 'likes_count']
        user = serializers.HiddenField(
            default=serializers.CurrentUserDefault()
        )

    def get_likes_count(self, obj):
        return obj.like_set.count()

    # def perform_create(self, serializer):
    #     serializer.save(user_id=self.request.user.id)
