import datetime

# from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Genre(models.Model):
    """Модель жанров."""
    name = models.CharField(
        verbose_name='Название', max_length=256, unique=True
    )
    slug = models.SlugField(verbose_name='Слаг', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель категорий."""
    name = models.CharField(
        verbose_name='Название', max_length=256, unique=True
    )
    slug = models.SlugField(verbose_name='Слаг', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Каттегории'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Моедль произведений."""
    # rating хотел сделать на уровне БД, проще сделать на уровне сериализатора
    name = models.CharField(max_length=256, verbose_name='Название')
    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=[
            MinValueValidator(1890),
            MaxValueValidator(datetime.datetime.now().year)
        ]
    )
    description = models.TextField(verbose_name='Описание', blank=True)
    genre = models.ManyToManyField(
        Genre, through='TitleGenre'
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='category'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    """Промежуточная таблица для Title и Genre"""
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Жанр и произведение'
        verbose_name_plural = 'Жанры и произведениея'

    def __str__(self):
        return f"Произведение: {self.title}, Жанр: {self.genre}"


class Review(models.Model):
    """Модель отзывов."""
    CHOICES_SCORE = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10)
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='title'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviwes_author'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг', choices=CHOICES_SCORE
    )
    pub_date = models.DateTimeField(
        verbose_name='', auto_now_add=True, editable=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        # Один из вариантов фикса ошибки который не сработал
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['title', 'author'],
        #         name='unique_review'
        #     ),
        # ]

    def __str__(self):
        return self.text

    # Один из вариантов фикса ошибки который не сработал
    # def clean(self):
    #     if Review.objects.filter(
    #         title=self.title, author=self.author
    #     ).exists():
    #         raise ValidationError(
    #             "Вы уже оставляли отзыв на это произведение."
    #         )
    #     super().clean()


class Comment(models.Model):
    """Модель комментрий."""
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments_author'
    )
    pub_date = models.DateTimeField(
        verbose_name='', auto_now_add=True, editable=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
