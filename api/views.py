from django.utils.http import urlsafe_base64_decode
from rest_framework.filters import SearchFilter

from GizShare.permissions import IsOwnerOrReadOnly
from .models import (Category, InterestedCategory, Topic, CustomTopic, InterestedTopic, Post,
                     Comment, Like, CommentLike, Follower, PostViewer, Bookmark, Review,
                     Cart, Address, Order, PostImage, PostReport, CommentReport, Download)
from .serializers import (InterestedCategorySerializer, TopicSerializer,
                          CustomTopicSerializer, InterestedTopicSerializer, PostSerializer, CommentSerializer,
                          LikeSerializer, CommentLikeSerializer, FollowSerializer,
                          PostViewSerializer, BookMarkSerializer, ReviewSerializer, CartSerializer,
                          AddressSerializer, OrderSerializer, FollowGetSerializer, CategorySerializer,
                          PostReportSerializer,
                          CommentReportSerializer, DownloadSerializer)
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Count, Prefetch, Avg, Q
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from user.models import User
from user.serializers import UserSerializer
from .filters import CategoryFilter, TopicFilter, InterestedCategoryFilter, InterestedTopicFilter, PostFilter, \
    PostElasticSearchFilter


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        followers = Follower.objects.filter(following_user=self.request.user)
        following = Follower.objects.filter(user=self.request.user)
        post = Post.objects.filter(user=self.request.user)

        followers_count = followers.count()
        following_count = following.count()
        post_count = post.count()

        follower_serializer = FollowSerializer(followers, many=True)
        following_serializer = FollowSerializer(following, many=True)

        data = {
            'followers': follower_serializer.data,
            'following': following_serializer.data,
            'followers_count': followers_count,
            'following_count': following_count,
            'post_count': post_count
        }

        return Response(data)


class CategoryView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating PostLike objects."""
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (IsAdminUser,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', ]


class InterestCategoryView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating interested categories for a user."""
    serializer_class = InterestedCategorySerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = InterestedCategoryFilter

    def get_queryset(self):
        return InterestedCategory.objects.filter(user=self.request.user).annotate(
            total_post=Count('category__post_category'))

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(InterestCategoryView, self).get_serializer(*args, **kwargs)


class TopicView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating topics."""
    serializer_class = TopicSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Topic.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_class = TopicFilter


class CustomTopicView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating custom user topics."""
    serializer_class = CustomTopicSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CustomTopic.objects.filter(user=self.request.user)


class InterestTopicView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating interested topics for a user."""
    serializer_class = InterestedTopicSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = InterestedTopicFilter

    def get_queryset(self):
        return InterestedTopic.objects.filter(user=self.request.user).annotate(total_post=Count('topic__post_topic'))

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(InterestTopicView, self).get_serializer(*args, **kwargs)


class PostView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating posts."""
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [PostElasticSearchFilter, DjangoFilterBackend]
    filterset_class = PostFilter

    def get_queryset(self):
        return Post.objects.prefetch_related(Prefetch('images', queryset=PostImage.objects.all()))


class PostEditView(generics.RetrieveUpdateDestroyAPIView):
    """This view endpoint for retrieving, updating, and deleting a post."""
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    filter_backends = [SearchFilter]
    lookup_field = 'id'

    def get_queryset(self):
        return Post.objects.select_related('user').prefetch_related(
            Prefetch('images', queryset=PostImage.objects.all()))


class CommentView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating comments."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Comment.objects.prefetch_related('replies').all()


class PostLikeView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating post likes."""
    serializer_class = LikeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Like.objects.select_related('user', 'post').all()


class PostUnlikeView(generics.RetrieveDestroyAPIView):
    """This view endpoint for retrieving and deleting a post like."""
    serializer_class = LikeSerializer
    lookup_field = 'id'
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        return Like.objects.select_related('user', 'post').all()


class CommentLikeView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating comment likes."""
    serializer_class = CommentLikeSerializer
    permission_classes = (IsAuthenticated,)
    queryset = CommentLike.objects.all()


class CommentUnlikeView(generics.RetrieveDestroyAPIView):
    """This view endpoint for retrieving and deleting a post like."""
    serializer_class = CommentLikeSerializer
    lookup_field = 'id'
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = CommentLike.objects.all()


class FollowView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating followers."""
    serializer_class = {
        'GET': FollowGetSerializer,
        'POST': FollowSerializer
    }
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Follower.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return self.serializer_class.get(self.request.method)


class FollowDetailView(generics.RetrieveDestroyAPIView):
    """This view endpoint for retrieving and deleting a follower."""
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    lookup_field = 'id'

    def get_queryset(self):
        return Follower.objects.select_related('following_user', 'user').all()


class PostViewerView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating post views."""
    serializer_class = PostViewSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return PostViewer.objects.select_related('post').annotate(
            view_count=Count('post__post_viewers')
        )


class BookmarkView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating bookmarks"""
    serializer_class = BookMarkSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('post').annotate(
            count=Count('post__post_bookmark')
        )


class EditBookmarkView(generics.RetrieveDestroyAPIView):
    """This view endpoint for retrieving and deleting a bookmark."""
    serializer_class = BookMarkSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    lookup_field = 'id'

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('user')


class ReviewView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating reviews."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Review.objects.annotate(
            average_rating=Avg('post__review__rating')
        ).order_by('-created_at')
        return queryset


class EditReviewView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        return Review.objects.select_related('user')


class CartView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating cart items."""
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


class RemoveCartView(generics.RetrieveDestroyAPIView):
    """This view endpoint for retrieving and deleting a cart item."""
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


class AddressView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating address."""
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class EditAddressView(generics.RetrieveUpdateDestroyAPIView):
    """This view endpoint for retrieving and deleting a cart address."""
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class OrderView(generics.ListCreateAPIView):
    """This view endpoint for listing and creating orders."""
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class EditOrderView(generics.RetrieveUpdateDestroyAPIView):
    """This view endpoint for retrieving, updating, and deleting an order."""
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class UserPostCategoryView(generics.ListAPIView):
    """This view endpoint for listing topics related to post the user is interested in."""
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Post.objects.filter(user=self.request.user)
        category_queryset = Category.objects.filter(post_category__in=queryset).annotate(
            category_count=Count('post_category')).distinct()
        return category_queryset


class UserPostTopicView(generics.ListAPIView):
    """This view endpoint for listing topics related to post the user is interested in."""
    serializer_class = TopicSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        topics = Topic.objects.filter(post_topic__user=self.request.user).distinct()
        return topics


class CategoryFilterView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']

    def get_queryset(self):
        queryset = Category.objects.all().annotate(category_count=Count('post_category'))

        return queryset.prefetch_related(
            Prefetch('post_category', queryset=Post.objects.filter(user=self.request.user)))

        return queryset


class OrganizationDetailView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(
            following_user__user=self.request.user,
            user_type=2
        )


class PostFollowerView(APIView):
    serializer_class = PostSerializer

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        following_user_ids = self.request.user.follower_user.all().values_list("following_user_id", flat=True)

        following_user_ids = list(following_user_ids) + [self.request.user.id]

        posts = Post.objects.select_related('user').prefetch_related(
            Prefetch('images', queryset=PostImage.objects.all())
        ).filter(user__in=following_user_ids)

        post_serializer = PostSerializer(posts, many=True)

        data = {
            'posts': post_serializer.data,
        }

        return Response(data)


class PostInterestView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_topics = InterestedTopic.objects.filter(user=self.request.user).values_list('topic_id', flat=True)

        return Post.objects.exclude(user=self.request.user).filter(
            topic_id__in=user_topics
        ).distinct()


class PostDetailView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve post details based on UID.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        uidb64 = self.kwargs['uidb64']
        post_id = urlsafe_base64_decode(uidb64)
        return self.queryset.get(id=post_id)


class PostReportView(generics.ListCreateAPIView):
    serializer_class = PostReportSerializer
    permission_classes = [IsAuthenticated]
    queryset = PostReport.objects.all()


class CommentReportView(generics.ListCreateAPIView):
    serializer_class = CommentReportSerializer
    permission_classes = [IsAuthenticated]
    queryset = CommentReport.objects.all()


class DownloadView(generics.ListCreateAPIView):
    serializer_class = DownloadSerializer
    permission_classes = [IsAuthenticated]
    queryset = Download.objects.all()