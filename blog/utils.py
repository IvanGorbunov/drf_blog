from django.db.models import Q
from django.db.models.query import RawQuerySet
from django_filters import CharFilter
from django_filters.rest_framework import FilterSet
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from django.test import override_settings
from rest_framework.test import APITestCase

from django.utils.timezone import now as tz_now

from blog.models import User


def generate_uniq_code() -> str:
    return str(tz_now().timestamp()).replace('.', '')


class MultiSerializerViewSet(ModelViewSet):
    filtersets = {
        'default': None,
    }
    serializers = {
        'default': Serializer,
    }

    @property
    def filterset_class(self):
        return self.filtersets.get(self.action) or self.filtersets.get('default')

    @property
    def serializer_class(self):
        return self.serializers.get(self.action) or self.serializers.get('default', Serializer)

    def get_response(self, data=None):
        return Response(data)

    def get_valid_data(self, many=False):
        serializer = self.get_serializer(data=self.request.data, many=many)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


@override_settings(SQL_DEBUG=False)
class TestCaseBase(APITestCase):
    """
    Базовый (без авторизации)
    """
    CONTENT_TYPE_JSON = 'application/json'

    def check_status(self, response, status):
        self.assertEqual(response.status_code, status, response.data)

    def generate_uniq_code(self):
        return generate_uniq_code()


class WithLoginTestCase(TestCaseBase):
    """
    С авторизацией
    """
    @classmethod
    def setUpClass(cls):
        user, is_create = User.objects.get_or_create(username='admin')
        if is_create:
            user.set_password('admin')
            user.save()
        cls.user = user
        cls.token, _ = Token.objects.get_or_create(user=user)
        super().setUpClass()

    def setUp(self) -> None:
        self.auth_user(self.user)
        super().setUp()

    def auth_user(self, user):
        """
        Авторизация
        """
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')


class SearchFilterSet(FilterSet):
    search_fields = ()
    search_method = 'icontains'
    q = CharFilter(method='filter_search', help_text='Поиск')

    def filter_search(self, queryset, name, value):
        if value:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f'{field}__{self.search_method}': value})
            queryset = queryset.filter(q_objects)
        return queryset.distinct()


def find_children(parent: dict, items: RawQuerySet) -> None:
    """
    Рекурсивный поиск дочерних элементов
    """
    for item in items:  # type ArticleComment
        if item.parent_id == parent['id']:
            comment = {
                'id': item.id,
                'article_id': item.article_id,
                'comment': item.comment,
                'parent_id': item.parent_id,
                'level': item.level,
                'is_root': item.is_root,
                'user_id': item.user_id,
                'create_dt': item.create_dt,
                'children': [],
            }
            parent['children'].append(comment)
            find_children(comment, items)



