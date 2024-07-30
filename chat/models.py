from django.db import models
from user.models import User
from django.utils import timezone
from .choices import MassageTypeChoices
from django.db.models import Q


# Create your models here.

class ConversationManager(models.Manager):

    def by_user_qs(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def by_user(self, user):
        qs = self.by_user_qs(user) \
            .select_related('first', 'first__userprofile', 'second', 'second__userprofile', 'message') \
            .only(
            'first__first_name',
            'first__last_name',
            'first__id',
            'second__first_name',
            'second__last_name',
            'second__id',
            'unread_first',
            'unread_second',
            'id', 'message', )
        return qs

    def get_or_new(self, first_id, second_id):  # get_or_create
        if first_id == second_id:
            return None, False
        qlookup1 = Q(first_id=first_id) & Q(second_id=second_id)
        qlookup2 = Q(first_id=second_id) & Q(second_id=first_id)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        qs = qs.select_related('first', 'second', 'message') \
            .only(
            'first__first_name',
            'first__last_name',
            'first__id',
            'second__first_name',
            'second__last_name',
            'second__id',
            'unread_first',
            'unread_second',
            'id', 'message', )
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            try:
                if first_id != second_id:
                    obj = self.model(
                        first_id=first_id,
                        second_id=second_id
                    )
                    obj.save()
                    return obj, True
            except Exception as e:
                return None, False
            return None, False


class Conversation(models.Model):
    first = models.ForeignKey(User, related_name='first', on_delete=models.CASCADE)
    second = models.ForeignKey(User, related_name='second', on_delete=models.CASCADE)
    unread_first = models.IntegerField(default=0)
    unread_second = models.IntegerField(default=0)
    at_deleted_first = models.DateTimeField(default=timezone.now)
    at_deleted_second = models.DateTimeField(default=timezone.now)
    message = models.ForeignKey('chat.UserMessage', null=True, on_delete=models.SET_NULL, related_name='last_message')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    objects = ConversationManager()

    def __str__(self):
        return "pk {}   :   {} - {}".format(self.pk, self.first, self.second)


class CustomDateTimeField(models.DateTimeField):
    def value_to_string(self, obj):
        val = self.value_from_object(obj)
        return '' if val is None else val.isoformat()


class UserMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='user', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='chat_file', null=True, blank=True)
    ratio = models.DecimalField(max_digits=2, decimal_places=1, default=1.0)
    message = models.TextField()
    m_type = models.IntegerField(choices=MassageTypeChoices.choices, default=MassageTypeChoices.TEXT_MESSAGE)
    timestamp = models.DateTimeField(auto_now_add=True)
