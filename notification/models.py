from django.db import models
from user.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class TimeAt(models.Model):
    created_at = models.DateTimeField(verbose_name="Created At", default=timezone.now)
    updated_at = models.DateTimeField(verbose_name="Updated At", default=timezone.now)

    class Meta:
        abstract = True


class NotificationType(models.IntegerChoices):
    FOLLOW = 1
    NEW_POST = 2
    LIKE_POST = 3
    USER_VERIFICATION = 4

class Notification(TimeAt):
    verb = models.IntegerField(choices=NotificationType.choices, help_text=NotificationType.choices, null=True)

    sender_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    sender_object_id = models.PositiveIntegerField(null=True)
    sender = GenericForeignKey('sender_content_type', 'sender_object_id')

    target_content_type = models.ForeignKey(ContentType, blank=True, null=True, related_name='target',
                                            on_delete=models.CASCADE, db_index=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
