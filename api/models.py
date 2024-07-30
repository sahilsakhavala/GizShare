from django.db import models
from user.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from .utils import validate_image


class TimeAt(models.Model):
    created_at = models.DateTimeField(verbose_name="Created At", default=timezone.now)
    updated_at = models.DateTimeField(verbose_name="Updated At", default=timezone.now)

    class Meta:
        abstract = True


CATEGORY_CHOICES = [
    ('articles', 'Articles'),
    ('books', 'Books'),
    ('case_studies', 'Case Studies'),
    ('certifications', 'Certifications'),
    ('dissertations_assignments', 'Dissertations and Assignments'),
    ('handbooks', 'Handbooks'),
    ('historical_items', 'Historical Items'),
    ('interviews', 'Interviews'),
    ('journals', 'Journals'),
    ('observations', 'Observations'),
    ('official_publications', 'Official Publications'),
    ('poems', 'Poems'),
    ('reports', 'Reports'),
    ('research', 'Research'),
    ('surveys', 'Surveys'),
    ('templates', 'Templates'),
]


class Category(models.Model):
    name = models.CharField(max_length=120, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.get_name_display()


class InterestedCategory(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='interested_category', on_delete=models.CASCADE)

    def __str__(self):
        return '{} '.format(self.pk)


class Topic(TimeAt):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.name


class CustomTopic(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return '{} '.format(self.pk)


class InterestedTopic(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interested_topic')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return '{} '.format(self.pk)


class Post(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='post_category', null=True,
                                 default=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True, related_name='post_topic')
    custom_topic = models.ForeignKey(CustomTopic, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=120, null=True, blank=True)
    hashtag = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return '{} '.format(self.pk)


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to="post_image", validators=[validate_image])


class PostViewer(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_viewers')

    def __str__(self):
        return '{} '.format(self.pk)


class Like(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')

    def __str__(self):
        return '{} '.format(self.pk)


class Comment(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()

    def __str__(self):
        return '{} '.format(self.pk)


class CommentLike(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    def __str__(self):
        return '{} '.format(self.pk)


class Follower(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_user')
    following_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_user')
    notification_target = GenericRelation("notification.Notification", object_id_field='target_object_id',
                                          content_type_field='target_content_type')

    def __str__(self):
        return '{} '.format(self.user)


class Bookmark(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_bookmark', null=True, blank=True)

    def __str__(self):
        return '{} '.format(self.pk)


class ReviewType(models.IntegerChoices):
    N = 1
    O = 2
    B = 3
    E = 4
    L = 5


class Review(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(choices=ReviewType.choices, help_text=ReviewType.choices, null=True)
    content = models.TextField(max_length=500)

    def __str__(self):
        return '{} '.format(self.pk)


class Cart(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField()

    def __str__(self):
        return '{} '.format(self.pk)


class Address(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return '{}'.format(self.pk)


class OrderType(models.IntegerChoices):
    PENDING = 1
    REJECTED = 2
    CONFIRMED = 3


class Order(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    status = models.IntegerField(choices=OrderType.choices, default=OrderType.PENDING, help_text=OrderType.choices,
                                 null=True)

    def __str__(self):
        return '{} - {}'.format(self.pk, self.user)


class PostReport(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reported_on = models.DateTimeField(default=timezone.now)


class CommentReport(TimeAt):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reported_on = models.DateTimeField(default=timezone.now)


class Download(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    download_on = models.DateTimeField()