from rest_framework import serializers
from .models import (Category, InterestedCategory, Topic, InterestedTopic, CustomTopic, Post, Comment,
                     Like, CommentLike, Follower, PostViewer, Bookmark, Review, Cart, PostReport, CommentReport,
                     Address, Order, PostImage, Download)
from user.models import User, DeviceDetails
from rest_framework.exceptions import ValidationError
from notification.genrator import follow_notification
from .tasks import send_post_notification_email
import django


class InterestedCategoryBulkCreateSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        with django.db.transaction.atomic():
            instances = [InterestedCategory(**item) for item in validated_data]
            InterestedCategory.objects.filter(user=self.context['request'].user).delete()
            created_instances = InterestedCategory.objects.bulk_create(instances)
        return created_instances


class InterestedCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    total_post = serializers.IntegerField(read_only=True)

    class Meta:
        model = InterestedCategory
        fields = ['user', 'category', 'total_post']
        read_only_fields = ['id', ]
        list_serializer_class = InterestedCategoryBulkCreateSerializer


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'category', 'name']


class CustomTopicSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = CustomTopic
        fields = ['id', 'user', 'name']


class InterestedTopicBulkCreateSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        with django.db.transaction.atomic():
            instances = [InterestedTopic(**item) for item in validated_data]
            InterestedTopic.objects.filter(user=self.context['request'].user).delete()
            created_instances = InterestedTopic.objects.bulk_create(instances)
        return created_instances


class InterestedTopicSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    total_post = serializers.IntegerField(read_only=True)

    class Meta:
        model = InterestedTopic
        fields = ['id', 'user', 'topic', 'total_post']
        read_only_fields = ['id', ]
        list_serializer_class = InterestedTopicBulkCreateSerializer


class PostImageSerializers(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'category', 'topic', 'hashtag', 'description', 'price',  'images',
                  'images']

    def create(self, validated_data):
        uploaded_images = validated_data.pop("images")
        post = Post.objects.create(**validated_data)

        send_post_notification_email.delay(post.id)

        PostImage.objects.bulk_create([
            PostImage(post=post, image=image) for image in uploaded_images
        ])

        return post

    def to_representation(self, instance):
        """Convert `images` field to read-only format."""
        ret = super().to_representation(instance)
        ret['images'] = PostImageSerializers(instance.images.all(), many=True).data
        return ret


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'parent_comment', 'content']


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Like
        fields = ['id', 'user', 'post']

    def validate(self, data):
        user = data.get('user')
        post = data.get('post')

        if post.user == user:
            raise ValidationError("You cannot like your own post.")

        return data


class CommentLikeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'comment']


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Follower
        fields = ['id', 'user', 'following_user']

    def create(self, validated_data):
        instance = super(FollowSerializer, self).create(validated_data)
        follow_notification(instance)
        return instance


class FollowGetSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Follower
        fields = ['id', 'user', 'following_user', 'followers_count', 'following_count']


class CategorySerializer(serializers.ModelSerializer):
    category_count = serializers.IntegerField(read_only=True)
    post_category = PostSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'category_count', 'post_category']


class PostViewSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    view_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PostViewer
        fields = ['id', 'user', 'post', 'view_count']


class BookMarkSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'post', 'count']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'post', 'rating', 'content', 'average_rating']


class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'post', 'quantity', 'total_price']

    def create(self, validated_data):
        user = validated_data.get('user')
        post = validated_data.get('post')
        quantity = validated_data.get('quantity')

        cart_item, created = Cart.objects.update_or_create(
            user=user,
            post=post,
            defaults={'quantity': quantity}
        )

        return cart_item

    def get_total_price(self, obj):
        print(obj.post.price)
        return obj.post.price * obj.quantity

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_price'] = self.get_total_price(instance)
        return representation


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ['created_at', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = ['id', 'user', 'post', 'quantity', 'address']


class PostReportSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PostReport
        fields = ['id', 'user', 'post']

    def validate(self, data):
        user = data.get('user')
        post = data.get('post')

        if PostReport.objects.filter(user=user, post=post).exists():
            raise ValidationError('You have already reported this post.')

        return data


class CommentReportSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CommentReport
        fields = ['id', 'user', 'comment']

    def validate(self, data):
        user = data.get('user')
        comment = data.get('comment')

        if CommentReport.objects.filter(user=user, comment=comment).exists():
            raise ValidationError('You have already reported this comment.')

        return data


class DownloadSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Download
        fields = ['id', 'user', 'post', 'download_on']