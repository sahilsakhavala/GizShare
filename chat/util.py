from channels.db import database_sync_to_async
from django.db.models import F
from rest_framework.fields import DateTimeField

from chat.exceptions import ClientError
from .models import Conversation, UserMessage

TYPE_MESSAGE = "chat_message"
TYPE_JOIN = "chat_join"
TYPE_RECONNECT = "chat_reconnect"
TYPE_LEAVE = "chat_leave"


def get_message(user_message, conversation_id):
    return {
        'type': TYPE_MESSAGE,
        'message': user_message.message,
        # 'image': user_message.image.url if user_message.image else None,
        'ratio': float(user_message.ratio),
        'user': user_message.user.id,
        'id': user_message.id,
        'timestamp': DateTimeField().to_representation(user_message.timestamp),
        'm_type': user_message.m_type,
        'conversation': conversation_id,
    }


def get_user_with(dic, user_id):
    dic['user_with'] = user_id
    return dic


@database_sync_to_async
def get_conversation(user, conversation_id):
    try:
        conversation = Conversation.objects.by_user(user.id).get(pk=conversation_id)
    except Conversation.DoesNotExist:
        raise ClientError("We haven't find the conversation.")
    user = conversation.second if conversation.first_id == user.id else conversation.first

    data = {
        'user': user.id,
        'id': conversation.pk,
        'name': '{first_name} {last_name}'.format(first_name=user.first_name, last_name=user.last_name),
        # 'image': user.userprofile.image.name if user.userprofile.image else None,

    }
    return conversation, data


def get_con(rooms, conversation_id):
    for item in rooms:
        print('item_id', item.id)
        print('item', item)
        if item.id == conversation_id:
            return item
    print('yes')
    return None


@database_sync_to_async
def save_message(conversation, user, m_type, message, ratio):
    message = UserMessage.objects.create(user=user, conversation_id=conversation.id, message=message,
                                         m_type=m_type, ratio=ratio)

    if conversation.second_id == user.id:
        user_with = conversation.first_id
        last_seen = conversation.first.userprofile.last_seen
        conversation.unread_first = F('unread_first') + 1
        conversation.unread_second = 0

    else:
        user_with = conversation.second_id
        conversation.unread_first = 0
        last_seen = conversation.second.userprofile.last_seen
        conversation.unread_second = F('unread_second') + 1
    conversation.message = message
    conversation.save(update_fields=['unread_first', 'unread_second', 'message'])
    return message, user_with, last_seen


@database_sync_to_async
def get_messages(user_id, last_id, conversation):
    messages = []
    if conversation.first_id == user_id:
        user_with = conversation.second.id
        print(user_with, '-----------user_with')
    else:
        user_with = conversation.first
        # print(user_with, '-----------user_with')

    for message in UserMessage.objects.filter(conversation_id=conversation.id, id__gt=last_id).iterator():
        dic = get_message(message, conversation.id)
        messages.append(get_user_with(dic, user_with))
    return messages


def get_room_name(user_id):
    return 'chat_%s' % user_id
