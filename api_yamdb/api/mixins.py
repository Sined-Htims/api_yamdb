from rest_framework import mixins, viewsets


class ListCreateDeleteMixin(
    mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Миксин для доступа к списку, созданию и удалению данных БД.
    Для моделей Genre и Category.
    """
    pass
