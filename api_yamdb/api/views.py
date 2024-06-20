from django.contrib.auth.tokens import default_token_generator
from django.db.utils import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets  # exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from api import filtters, func, mixins
from api.permissions import IsAuthorOrModeratorOrAdmin, IsAdminUser
from api.serializers import (
    AuthSingnupSerializer, AuthTokenSerializer,
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleSerializer, TitleForListRetrieveSerializer,
    User, UserMeSerializer, UserSerializer
)
from reviews.models import Category, Comment, Genre, Review, Title


class AuthSignupViewSet(mixins.PostMixin):
    """Эндпоинт для регистрации пользователя."""
    queryset = User.objects.all()
    serializer_class = AuthSingnupSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        # Создаем пользователя по его данным и и отправляем код подтверждения
        # на указаный имейл.
        serializer = AuthSingnupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        try:
            user, reg = User.objects.get_or_create(
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

        # Было
        # if reg:
        #     return Response(serializer.data, status=status.HTTP_200_OK)
        # else:
        #     try:
        #         return Response(
        #             'Пользователь с таким username и email'
        #             ' уже существует, проверьте почту.',
        #             status=status.HTTP_200_OK
        #         )
        #     except IntegrityError:
        #         return Response(
        #             'Данный email или username занят',
        #             status=status.HTTP_400_BAD_REQUEST
        #         )


# Через миксин
class AuthTokenViewSet(mixins.PostMixin):
    """Эндпоинт для получения токена."""
    serializer_class = AuthTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Другой способ через функцию
# from rest_framework import views
# class AuthTokenViewSet(views.APIView):
#     """Эндпоинт для получения токена."""
#     def post(self, request):
#         serializer = AuthTokenSerializer(data=request.data)
#         if serializer.is_valid():
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#          return Response(
#             serializer.errors, status=status.HTTP_400_BAD_REQUEST
#         )


class CategoryViewSet(mixins.ListCreateDeleteMixin):
    """Эндпоинт для работы с объектами модели Category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.action == 'list':
            return super().get_permissions()
        return (IsAdminUser(),)


class CommentViewSet(viewsets.ModelViewSet):
    """Эндпоинт для работы с объектами модели Comment."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    )

    def get_review(self):
        """Получает объект модели Review по id или выдает ошибку."""
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        # Получаем все коментарии к определенному отзыву.
        return Comment.objects.filter(review=self.get_review())

    # Т.к. данный пермишен в permission_classes не работает с retrieve
    # нужно еще раз его прописать.
    def get_permissions(self):
        if self.action == 'retrieve':
            return (permissions.IsAuthenticatedOrReadOnly(),)
        return super().get_permissions()

    def perform_create(self, serializer):
        # Записываем: Кто и к какому отзыву был добавлен конмментарий.
        return serializer.save(
            author=self.request.user, review=self.get_review()
        )

    # Кринж убирание PUT-запроса из Viewset'а
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if not partial:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


class GenreViewSet(mixins.ListCreateDeleteMixin):
    """Эндпоинт для работы с объектами модели Genre."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.action == 'list':
            return super().get_permissions()
        return (IsAdminUser(),)


class ReviewViewSet(viewsets.ModelViewSet):
    """Эндпоинт для работы с объектами модели Review."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    )

    def get_title(self):
        """Получает объект модели Title по id или выдает ошибку."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        # Получаем все отзывы для определенного произведения.
        return Review.objects.filter(title=self.get_title())

    # Т.к. данный пермишен в permission_classes не работает с retrieve
    # нужно еще раз его прописать.
    def get_permissions(self):
        if self.action == 'retrieve':
            return (permissions.IsAuthenticatedOrReadOnly(),)
        return super().get_permissions()

    def perform_create(self, serializer):
        # Делаем проверку на существоание отзыва от пользователя, если
        # отзыв уже существует то выдаем ошибку.
        # Может через get_or_create? В def create serializers
        # if Review.objects.filter(author=self.request.user).exists():
        #     raise exceptions.ValidationError(
        #         "Вы уже оставили отзыв на данное произведение"
        #     )
        # Если пользователь не создавал отзыв, то автоматически записываем:
        # Кто и к какому произведению написали отзыв.
        return serializer.save(
            author=self.request.user, title=self.get_title()
        )

    # Кринж убирание PUT-запроса из Viewset'а
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if not partial:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


class TitleViewSet(viewsets.ModelViewSet):
    """Эндпоинт для работы с объектами модели Title."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filtters.TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleForListRetrieveSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return super().get_permissions()
        return (IsAdminUser(),)

    # Кринж убирание PUT-запроса из Viewset'а
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if not partial:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    # Почему это kwargs['partial'] = True не дефолт?
    # В джанго написано что дефолт
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    """Эндпоинт для работы с объектами модели User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def get_permissions(self):
        # Меняем права доступа для эндпоинта users/me/
        if self.action == 'user_me':
            return (permissions.IsAuthenticated(),)
        else:
            return (IsAdminUser(),)

    # Почему это kwargs['partial'] = True не дефолт?
    # В джанго написано что дефолт
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    # Кринж убирание PUT-запроса из Viewset'а
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if not partial:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    @action(
        methods=['GET', 'PUT', 'PATCH', 'DELETE'], detail=False, url_path='me'
    )
    def user_me(self, request):
        """View-функция для эндпоинта users/me/."""
        if request.method == 'GET':
            serializer = UserMeSerializer(request.user)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            serializer = UserMeSerializer(
                request.user, data=request.data,
                partial=request.method == 'PATCH'
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        # Для выполнения тестов, до этого в декораторе не было метода DELETE,
        # и тест выдавал ошибку 403, а постман выдавал 405
        # кода ниже не было.
        elif request.method == 'DELETE':
            return Response(
                'Метод \"DELETE\" не разрешен.',
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
