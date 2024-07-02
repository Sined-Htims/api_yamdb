from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers
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
        max_length=settings.USERNAME_MAX_LENGTH,
        validators=(validators.username_validator, validators.username_not_me),
        required=True,
    )
    email = serializers.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH,
        required=True,
    )


class AuthTokenSerializer(serializers.Serializer):
    """
    Сериализатор для ПОДТВЕРЖДЕНИЯ регистрации пользователя и выдачи токена.
    """
    username = serializers.CharField(
        max_length=150,
        write_only=True,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=39,
        write_only=True,
        required=True
    )


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
        # read_only_fields = ('title',)
        # # Один из вариантов фикса ошибки который не сработал
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
        """Расчет средней оценки произведения"""
        review = Review.objects.filter(
            title_id=obj.id).aggregate(res=Avg('score'))
        return review.get('res')

    def create(self, validated_data):
        # Создание записи в модели Title.
        # Сохраняем в переменные полученные данные.
        genre_list = validated_data.pop('genre')
        category_name = validated_data.pop('category')
        # Получаем объект модели Category или выдаем ошибку.
        current_category = get_object_or_404(Category, name=category_name)
        # Создаем объект на основе введенных данных, без жанров.
        title = Title.objects.create(
            category=current_category, **validated_data
        )
        # Распаковываем все жанры в переменную.
        for genre_dict in genre_list:

            # Почему словарь в for сразу распаковался?
            # print(genre_dict)
            # genre = genre_dict.pop('Genre')
            # print(genre)

            # Получаем объект модели Genre или выдаем ошибку.
            current_genre = get_object_or_404(Genre, name=genre_dict)
            # Добавляем к произведению жанры.
            TitleGenre.objects.create(title=title, genre=current_genre)
        return title


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
