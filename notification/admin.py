from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender_object_id', 'receiver_id', 'verb', 'target', 'created_at']
    search_fields = ['id', 'receiver__email', 'verb']
    list_filter = ['created_at', 'verb']
    list_display_links = list_display
