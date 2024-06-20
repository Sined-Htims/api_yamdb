from django.urls import include, path
from rest_framework import routers

from api.views import (
    AuthSignupViewSet, AuthTokenViewSet, CategoryViewSet,
    CommentViewSet, GenreViewSet, ReviewViewSet, TitleViewSet,
    UserViewSet
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'auth/signup', AuthSignupViewSet, basename='signup')
# Эндпоинт auth/token/ если делаем view через миксин
router.register(r'auth/token', AuthTokenViewSet, basename='token')
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'titles', TitleViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet
)


urlpatterns = [
    path('', include(router.urls)),
    # Эндпоинт auth/token/ если делаем view через функцию
    # path('auth/token/', AuthTokenViewSet.as_view(), name='token'),
]
