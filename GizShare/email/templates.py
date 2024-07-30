from django.template.loader import render_to_string
from GizShare.email.backend import get_info_connection
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.template.loader import render_to_string
from django.urls import reverse


def verify_email(request, user):
    connection, from_email = get_info_connection()
    current_site = f'http://{get_current_site(request=request).domain}/'
    uid_bytes = force_bytes(user.pk)
    uid_base64 = urlsafe_base64_encode(uid_bytes)
    reset_link = f"{current_site}v1/verify_email/{uid_base64}/"
    subject = "Email Verification - GizShare"
    to = user.email
    data = {'current_site': current_site, 'reset_link': reset_link}
    html_message = render_to_string('send_mail.html', context=data)
    body = 'Please verify your email address by clicking the link provided in this email. Additionally, you can use the following link to reset your password: ' + reset_link

    email_message = EmailMultiAlternatives(subject, body, from_email, [to], connection=connection)
    email_message.attach_alternative(html_message, "text/html")
    email_message.send()

    return render(request, 'send_mail.html', {'reset_link': reset_link})


def reset_password_mail(request, user):
    current_site_domain = f'http://{get_current_site(request=request).domain}/'
    uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
    token = PasswordResetTokenGenerator().make_token(user)
    forget_password_link = f'{current_site_domain}v1/request_reset_password/{uidb64}/{token}/'
    print(forget_password_link)
    data = {'forget_password_link': forget_password_link, 'current_site': current_site_domain, 'email': user.email}
    body = render_to_string('reset_password.html', context=data)
    to = user.email
    subject = 'Reset your password - GizShare'
    connection, from_email = get_info_connection()
    email_message = EmailMultiAlternatives(subject, body, from_email, [to], connection=connection)
    email_message.content_subtype = 'html'
    email_message.send()

    return render(request, 'reset_password.html', {'forget_password_link': forget_password_link})


def send_email_to_interested_users(request, post, interested_users):
    subject = f"New post in {post.category.name} category: {post.topic}"
    current_site = get_current_site(request)
    current_site_domain = f'http://{current_site.domain}/'

    # Generate a unique link for each interested user to view the post
    for user_email in interested_users:
        uidb64 = urlsafe_base64_encode(smart_bytes(post.id))  # Use post.id or post.uid based on your setup
        post_notification_link = f'{current_site_domain}v1/post_notification/{uidb64}/'

        message_html = render_to_string('post.html', {
            'post_category_name': post.category.name,
            'post_url': post_notification_link,
            'post_description': post.description,
            'post_image': post.images.first().image.url if post.images.first() else '',
        })

        connection, from_email = get_info_connection()

        email_message = EmailMultiAlternatives(
            subject=subject,
            body=message_html,
            from_email=from_email,
            to=[user_email],
            connection=connection
        )
        email_message.content_subtype = 'html'
        email_message.send(fail_silently=False)
