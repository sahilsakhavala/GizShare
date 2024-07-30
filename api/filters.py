from django.db.models import Count, Q
from django.utils import timezone
from django_filters import rest_framework as filters
from .models import Category, Topic, Post
from rest_framework.filters import SearchFilter
from elasticsearch_dsl import Q
from django.db.models import Case, When
from elasticsearch.exceptions import NotFoundError
from .documents import PostDocument
from elasticsearch_dsl.query import MultiMatch


class CategoryFilter(filters.FilterSet):
    category_ids = filters.CharFilter(method='category_ids_filter', label='Category ids')

    class Meta:
        model = Category
        fields = ['category_ids']

    def category_ids_filter(self, queryset, name, value):
        category_ids = value.split(',')
        return queryset.exclude(pk__in=category_ids)


class TopicFilter(filters.FilterSet):
    category_ids = filters.ModelMultipleChoiceFilter(field_name='category__id', to_field_name='id',
                                                     queryset=Category.objects.all())
    topic_ids = filters.CharFilter(method='filter_by_topic_ids', label='Topic IDs')

    class Meta:
        model = Topic
        fields = ['category_ids', 'topic_ids']

    def filter_by_topic_ids(self, queryset, name, value):
        topic_ids = value.split(',')
        return queryset.filter(id__in=topic_ids)


class InterestedCategoryFilter(filters.FilterSet):
    start_date = filters.DateFilter(lookup_expr=('gte'), field_name='created_at__date', label='start_date')
    end_date = filters.DateFilter(lookup_expr=('lte'), field_name='created_at__date', label='end_date')


class InterestedTopicFilter(filters.FilterSet):
    start_date = filters.DateFilter(lookup_expr=('gte'), field_name='created_at__date', label='start_date')
    end_date = filters.DateFilter(lookup_expr=('lte'), field_name='created_at__date', label='end_date')


STATUS_CHOICES = (
    ('top', 'Top'),
    ('best', 'Best'),
    ('recent', 'Recent'),
)


class PostFilter(filters.FilterSet):
    status = filters.ChoiceFilter(field_name='status', choices=STATUS_CHOICES, method='filter_for_post', label='status')
    is_mine = filters.BooleanFilter(field_name='is_mine', method='filter_for_own_post', label='is_mine')
    is_followers = filters.BooleanFilter(field_name='is_followers', method='filter_for_followers_post',
                                         label='is_followers')

    class Meta:
        model = Post
        fields = ['status', 'category', 'is_mine', 'is_followers']

    def filter_for_post(self, queryset, name, value):
        following_user_ids = self.request.user.follower_user.all().values_list("following_user_id", flat=True)
        days = timezone.now() - timezone.timedelta(hours=24)

        queryset = queryset.filter(Q(user_id__in=following_user_ids) | Q(user=self.request.user))

        if value == 'top':
            queryset = queryset.annotate(num_likes=Count('post_likes')).order_by('-num_likes', '-created_at')

        elif value == 'best':
            queryset = queryset.filter(created_at__gte=days).order_by('-created_at')

        elif value == 'recent':
            queryset = queryset.order_by('-created_at')

        return queryset.distinct()

    def filter_for_own_post(self, queryset, name, value):
        return queryset.filter(user=self.request.user)

    def filter_for_followers_post(self, queryset, name, value):
        following_user_ids = self.request.user.follower_user.all().values_list("following_user_id", flat=True)
        return queryset.filter(user_id__in=following_user_ids)


class PostElasticSearchFilter(SearchFilter):
    def get_search_fields(self, view, request):
        return super().get_search_fields(view, request)

    def filter_queryset(self, request, queryset, view):
        query = request.query_params.get('search', None)
        if query:
            try:
                search = PostDocument.search().query(
                    MultiMatch(fields=['title', 'hashtag', 'category'], type='phrase_prefix', query=query))
                response = search.execute()
                hits = response.hits
                relevant_ids = [hit.meta.id for hit in hits]
                post = Case(
                    *[When(id=id, then=p) for p, id in enumerate(relevant_ids)])
                queryset = queryset.filter(id__in=relevant_ids).order_by(post)
                return queryset
            except NotFoundError as e:
                print(f"NotFoundError: {e}")
                return queryset.none()
            except Exception as e:
                print(f"Exception: {e}")
                return queryset.none()
        else:
            return queryset
