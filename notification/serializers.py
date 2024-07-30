from rest_framework import serializers
from .models import Notification


class NotificationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'sender_object_id', 'receiver_id']
