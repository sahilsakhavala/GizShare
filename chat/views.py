from .models import Conversation
from .serializers import ConversationSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class ConversationView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.by_user(self.request.user)
