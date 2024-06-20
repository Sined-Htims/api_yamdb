from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken  # RefreshToken
# Один из вариантов фикса ошибки который не сработал
# from rest_framework.validators import UniqueTogetherValidator

from reviews.models import (
    Category, Comment, Genre, Review, Title, TitleGenre
)
from users import validators

User = get_user_model()


class AuthSingnupSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""
    username = serializers.CharField(
        max_length=settings.USERNAME_MAX_LENGTH, required=True,
        validators=(validators.username_validator, validators.username_not_me),
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH, required=True,
    )


class AuthTokenSerializer(serializers.Serializer):
    """
    Сериализатор для ПОТДВЕРЖДЕНИЯ регистрации пользователя и выдачи токена.
    """
    username = serializers.CharField(max_length=150, write_only=True)
    confirmation_code = serializers.CharField(max_length=39, write_only=True)
    token = serializers.SerializerMethodField()
    # Если понадобится токен для обновления токена доступа:
    # refresh_token = serializers.SerializerMethodField()

    def validate(self, data):
        # Проверяем существует ли пользователь с веденным именем.
        username = data.get('username')
        user = get_object_or_404(User, username=username)
        # Получаем код подверждения веденный пользователем и проверяем на
        # соответствие с отправленным.
        confirmation_code = data.get('confirmation_code')
        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                'Указан неверный код подтверждения.'
            )
        return data

    def get_token(self, obj):
        # Генерируем токен доступа для пользователя.
        user = User.objects.get(username=obj['username'])
        token = AccessToken.for_user(user)
        return str(token)

    # def get_refresh_token(self, obj):
    #     # Генерируем обновляющий токен для смены токена доступа.
    #     # Думаю убрать т.к. на эндпоинте auth/token/ можно обновить токен,
    #     # с помощью того же кода подтверждения.
    #     user = User.objects.get(username=obj['username'])
    #     refresh = RefreshToken.for_user(user)
    #     return str(refresh)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для Category."""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для Comment."""
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для Genre."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для Review."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        # Один из вариантов фикса ошибки который не сработал
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=Review.objects.all(),
        #         fields=('title', 'author')
        #     )
        # ]


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для Title для не безопасных запросов."""
    rating = serializers.SerializerMethodField()
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )

    def get_rating(self, obj):
        """Расчет средней оценки произведения"""  # Хотел сделать в модели
        review = Review.objects.filter(
            title_id=obj.id).aggregate(res=Avg('score'))
        return review.get('res')

    def create(self, validated_data):
        # Создание записи в моделе Title.
        # Сохраняем в переменные полученные данные.
        genre_list = validated_data.pop('genre')
        category_name = validated_data.pop('category')
        # Один из вариантов фикса ошибки который не сработал
        # category_name = category.pop('name')
        # category_slug = category.pop('slug')
        # Получаем объект модели Category или выдаем ошибку.
        current_category = get_object_or_404(Category, name=category_name)
        # Создаем объект на основе введеных данных, без жанров.
        title = Title.objects.create(
            category=current_category, **validated_data
        )
        # Распаковываем все жанры в переменную.
        for genre_dict in genre_list:

            # Почему словарь в for сразу  распаковался?
            # print(genre_dict)
            # genre_name = genre_dict.pop('Genre')
            # print(genre_name)

            # Получаем объект модели Genre или выдаем ошибку.
            current_genre = get_object_or_404(Genre, name=genre_dict)
            # Добавляем к произведению жанры.
            TitleGenre.objects.create(title=title, genre=current_genre)
        return title

# Если бы нужно было в произведениях еще создавать категорию и жанры то,
# необходимо изменить поля сериализатора с serializers.SlugRelatedField,
# на вложенные (category=CategorySerializer()) сериализаторы и использовать
# метод get_or_create()


class TitleForListRetrieveSerializer(TitleSerializer):
    """
    Сериализатор для Title для запросов из серии SAFE_METHODS.
    Унаследованный от предыдущего сериализатора.
    """
    genre = GenreSerializer(many=True)
    category = CategorySerializer()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для User."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class UserMeSerializer(UserSerializer):
    """
    Сериализатор для эндпоинта 'users/me/'.
    Унаследованный от предыдущего сериализатора.
    """
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        read_only_fields = ('role',)
