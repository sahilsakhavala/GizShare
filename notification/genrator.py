from api.models import *
from user.models import *
from .models import Notification, NotificationType

from django.contrib.contenttypes.models import ContentType

try:
    USER_CONTENT_TYPE = ContentType.objects.get_for_model(User)
    FOLLOW_CONTENT_TYPE = ContentType.objects.get_for_model(Follower)
    POST_CONTENT_TYPE = ContentType.objects.get_for_model(Post)
    USER_VERIFICATION_TYPE = ContentType.objects.get_for_model(UserVerification)
except Exception as e:
    pass


def follow_notification(instance):
    Notification.objects.create(sender_object_id=instance.user_id,
                                sender_content_type=USER_CONTENT_TYPE,
                                verb=NotificationType.FOLLOW,
                                target_object_id=instance.id,
                                target_content_type=FOLLOW_CONTENT_TYPE,
                                receiver=instance.following_user)


def user_verification_notification(instance):
    Notification.objects.create(
        verb=NotificationType.USER_VERIFICATION,
        sender_content_type=USER_CONTENT_TYPE,
        sender_object_id=instance.user.id,
        target_content_type=USER_VERIFICATION_TYPE,
        target_object_id=instance.id,
        receiver=instance.user
    )