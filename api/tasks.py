from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from api.models import Post
from GizShare.email.backend import get_info_connection
from user.models import User


@shared_task
def send_post_notification_email(post_id):
    try:
        post = Post.objects.get(id=post_id)
        subject = f"New post in {post.category.name}"

        uidb64 = urlsafe_base64_encode(smart_bytes(post.id))
        post_notification_link = f'http://{settings.CURRENT_SITE}/v1/post_notification/{uidb64}/'

        interested_users = User.objects.filter(interestedcategory__category=post.category).exclude(
            id=post.user.id).distinct()

        connection, from_email = get_info_connection()

        for user in interested_users:
            message_html = render_to_string('post.html', {
                'post_category_name': post.category.name,
                'post_url': post_notification_link,
                'post_description': post.description,
                'post_image': post.images.first().image.url if post.images.first() else '',
            })

            email_message = EmailMultiAlternatives(
                subject=subject,
                body=message_html,
                from_email=from_email,
                to=[user.email],
                connection=connection
            )
            email_message.content_subtype = 'html'
            email_message.send(fail_silently=False)

            print(f"Email sent to {user.email}")

    except Post.DoesNotExist:
        print(f"Post with ID {post_id} does not exist.")
    except Exception as e:
        print(f"Error sending email notification: {e}")
