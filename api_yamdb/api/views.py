from django.contrib.auth.tokens import default_token_generator
from django.db.utils import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api import func, mixins
from api.filters import TitleFilter
from api.permissions import (
    IsAuthorOrModeratorOrAdmin, IsAdminUser, IsAdminOrReadOnly
)
from api.serializers import (
    AuthSingnupSerializer, AuthTokenSerializer,
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleSerializer, TitleForListRetrieveSerializer,
    User, UserMeSerializer, UserSerializer
)
from reviews.models import Category, Comment, Genre, Review, Title


class AuthSignupViewSet(views.APIView):
    """Эндпоинт для регистрации пользователя."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        # Создаем пользователя по его данным и и отправляем код подтверждения
        # на указанный имейл.
        serializer = AuthSingnupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        try:
            user, _ = User.objects.get_or_create(
                username=username, email=email
            )
        except IntegrityError:
            return Response(
                'Данный email или username занят',
                status=status.HTTP_400_BAD_REQUEST
            )
        token = default_token_generator.make_token(user)
        func.send_mail_with_code(email, token)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthTokenViewSet(views.APIView):
    """Эндпоинт для получения токена."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        # Получение токена на основе кода подтверждения и имени пользователя
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        # Проверка кода подтверждения
        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response(
                {'token': str(token)}, status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class CategoryViewSet(mixins.ListCreateDeleteMixin):
    """Эндпоинт для работы с объектами модели Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CommentViewSet(viewsets.ModelViewSet):
    """Эндпоинт для работы с объектами модели Comment."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    )
    # Указываем с какими методами запросов работает эндпоинт
    http_method_names = ['get', 'head', 'options', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'retrieve':
            return (permissions.IsAuthenticatedOrReadOnly(),)
        return super().get_permissions()

    def get_review(self):
        """Получает объект модели Review по id или выдает ошибку."""
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        # Получаем все комментарии к определенному отзыву.
        return Comment.objects.filter(review=self.get_review())

    def perform_create(self, serializer):
        # Записываем: Кто и к какому отзыву был добавлен комментарий.
        return serializer.save(
            author=self.request.user, review=self.get_review()
        )


class GenreViewSet(mixins.ListCreateDeleteMixin):
    """Эндпоинт для работы с объектами модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    """Эндпоинт для работы с объектами модели Review."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    )
    http_method_names = ['get', 'head', 'options', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'retrieve':
            return (permissions.IsAuthenticatedOrReadOnly(),)
        return super().get_permissions()

    def get_title(self):
        """Получает объект модели Title по id или выдает ошибку."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        # Получаем все отзывы для определенного произведения.
        return Review.objects.filter(title=self.get_title())

    def perform_create(self, serializer):
        # Если пользователь не создавал отзыв, то автоматически записываем:
        # Кто и к какому произведению написали отзыв.
        return serializer.save(
            author=self.request.user, title=self.get_title()
        )

    def create(self, request, *args, **kwargs):
        # Ограничиваем создание нескольких отзывов от одного пользователя
        # Выглядит как костыль, не особо на уровне модели, странно что через
        # сериализатор не работает
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {'error': 'Обзор на произведение от вас уже существует.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TitleViewSet(viewsets.ModelViewSet):
    """Эндпоинт для работы с объектами модели Title."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ['get', 'head', 'options', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in {'list', 'retrieve'}:
            return TitleForListRetrieveSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in {'list', 'retrieve'}:
            return super().get_permissions()
        return (IsAdminUser(),)


class UserViewSet(viewsets.ModelViewSet):
    """Эндпоинт для работы с объектами модели User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'head', 'options', 'post', 'patch', 'delete']

    @action(
        methods=['GET', 'PATCH',],
        detail=False,
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def user_me(self, request):
        """View-функция для эндпоинта users/me/."""
        if request.method == 'GET':
            serializer = UserMeSerializer(request.user)
            return Response(serializer.data)
        serializer = UserMeSerializer(
            request.user, data=request.data,
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
