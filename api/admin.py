from django.contrib import admin
from .models import (Category, InterestedCategory, Topic, InterestedTopic, CustomTopic, Post, PostImage, Comment,
                     Like, CommentLike, Follower, PostViewer, Bookmark,
                     Review, Cart, Address, Order, PostReport, CommentReport, Download)


@admin.register(Category)
class CategoryChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(InterestedCategory)
class InterestedCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category')


@admin.register(Topic)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_id', 'name']


@admin.register(CustomTopic)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'name']


@admin.register(InterestedTopic)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'topic_id']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'category_id', 'topic_id', 'title', 'hashtag', 'description', 'price', 'created_at']


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_id', 'image']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'post_id', 'parent_comment', 'content']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'post_id']


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'comment']


@admin.register(Follower)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'following_user_id']


@admin.register(PostViewer)
class PostViewerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'post_id']


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'post_id']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'post_id', 'rating', 'content']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'post_id', 'quantity']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'address_line1', 'address_line1', 'city', 'state', 'country', 'postal_code']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'post_id', 'quantity', 'address_id', 'status']


@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'post_id', 'reported_on']


@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'comment_id', 'reported_on']


@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'post_id', 'download_on']