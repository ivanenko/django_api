from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from posts.views import PostViewSet, analytics, UserViewSet
from rest_framework.authtoken import views


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)


urlpatterns = [
    path('analytics/', analytics),
    url(r'^', include(router.urls)),
    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
