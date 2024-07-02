import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтр для вьюсета произведений, с полями категория, жанр, название."""
    category = django_filters.CharFilter(field_name='category__slug')
    genre = django_filters.CharFilter(field_name='genre__slug')
    name = django_filters.CharFilter(field_name='name')

    class Meta:
        model = Title
        fields = ('name', 'genre', 'category', 'year')
