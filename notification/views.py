from .models import Notification
from .serializers import NotificationListSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class NotiFicationView(generics.ListAPIView):
    """This view endpoint for listing user notification"""
    serializer_class = NotificationListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user)
