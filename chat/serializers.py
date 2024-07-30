from rest_framework import serializers
from .models import UserMessage, Conversation
from django.db.models import Q


class UserMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMessage
        fields = '__all__'


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'first', 'second']

    class ConversationSerializer(serializers.ModelSerializer):
        class Meta:
            model = Conversation
            fields = ['id', 'first', 'second']

    def create(self, validated_data):
        first_user = validated_data.get('first')
        second_user = validated_data.get('second')

        if Conversation.objects.filter(
                Q(first=first_user, second=second_user) |
                Q(first=second_user, second=first_user)
        ).exists():
            raise serializers.ValidationError("Conversation between these users already exists.")

        conversation = Conversation.objects.create(first=first_user, second=second_user)
        return conversation
