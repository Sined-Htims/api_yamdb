# Почему если расставить импорты в соответствии со стандартами, то
# скрипт уже не работает?
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_yamdb.settings')
django.setup()

import csv
import chardet
from reviews.models import (
    Genre, Category, Title, TitleGenre, Review, Comment
)
from users.models import CustomUser


# Автоматически проверяем кодировку полученных данных
def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
    return result['encoding']


# Импортируем данные из CSV файла в модель CustomUser:
# Функция на вход должна получать путь до файла
def import_data_for_user(user_file_path):
    # Вызываем и запоминаем кодировку полученных данных
    encoding = detect_encoding(user_file_path)
    with open(user_file_path, 'r', encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            # Сопоставляем поля модели со столбцами CSV файла
            instance = CustomUser(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=row['role'],
                bio=row['bio'],
                first_name=row['first_name'],
                last_name=row['last_name'],
            )
            instance.save()


# Записываем путь до CSV файла
user_file_path = 'static/data/users.csv'
# Вызываем функцию
import_data_for_user(user_file_path)


# Все аналогично но для модели Category
def import_data_for_category(category_file_path):
    encoding = detect_encoding(category_file_path)
    with open(category_file_path, 'r', encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            instance = Category(
                id=row['id'],
                name=row['name'],
                slug=row['slug'],
            )
            instance.save()


category_file_path = 'static/data/category.csv'
import_data_for_category(category_file_path)


# Все аналогично но для модели Genre
def import_data_for_genre(genre_file_path):
    encoding = detect_encoding(genre_file_path)
    with open(genre_file_path, 'r', encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            instance = Genre(
                id=row['id'],
                name=row['name'],
                slug=row['slug'],
            )
            instance.save()


genre_file_path = 'static/data/genre.csv'
import_data_for_genre(genre_file_path)


# Все аналогично но для модели Title
def import_data_for_title(title_file_path):
    encoding = detect_encoding(title_file_path)
    with open(title_file_path, 'r', encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            instance = Title(
                id=row['id'],
                name=row['name'],
                year=row['year'],
                category_id=row['category'],
            )
            instance.save()


title_file_path = 'static/data/titles.csv'
import_data_for_title(title_file_path)


# Все аналогично но для модели TitleGenre
def import_data_for_genre_title(genre_title_file_path):
    encoding = detect_encoding(genre_title_file_path)
    with open(genre_title_file_path, 'r', encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            instance = TitleGenre(
                id=row['id'],
                title_id=row['title_id'],
                genre_id=row['genre_id'],
            )
            instance.save()


genre_title_file_path = 'static/data/genre_title.csv'
import_data_for_genre_title(genre_title_file_path)


# Все аналогично но для модели Review
def import_data_for_review(review_file_path):
    encoding = detect_encoding(review_file_path)
    with open(review_file_path, 'r', encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            instance = Review(
                id=row['id'],
                title_id=row['title_id'],
                text=row['text'],
                author_id=row['author'],
                score=row['score'],
                pub_date=row['pub_date'],
            )
            instance.save()


review_file_path = 'static/data/review.csv'
import_data_for_review(review_file_path)


# Все аналогично но для модели Comment
def import_data_for_comments(comments_file_path):
    encoding = detect_encoding(comments_file_path)
    with open(comments_file_path, 'r', encoding=encoding) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            instance = Comment(
                id=row['id'],
                review_id=row['review_id'],
                text=row['text'],
                author_id=row['author'],
                pub_date=row['pub_date'],
            )
            instance.save()


comments_file_path = 'static/data/comments.csv'
import_data_for_comments(comments_file_path)
