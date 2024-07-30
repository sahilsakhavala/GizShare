from django.contrib import admin
from django.contrib.admin import ModelAdmin
from chat.models import UserMessage, Conversation


class UserMessageAdmin(admin.TabularInline):
    model = UserMessage


@admin.register(UserMessage)
class UserMessageAdmin(ModelAdmin):
    list_display = ('id', 'conversation', 'timestamp')


@admin.register(Conversation)
class ThreadAdmin(ModelAdmin):
    list_display = ('id', 'first', 'second', 'timestamp')
    search_fields = ['id']
