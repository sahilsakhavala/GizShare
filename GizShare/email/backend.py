from django.conf import settings
from django.core.mail import get_connection


def get_info_connection():
    connection = get_connection(host=settings.EMAIL_HOST,
                                port=settings.EMAIL_PORT,
                                username=settings.EMAIL_HOST_USER,
                                password=settings.EMAIL_HOST_PASSWORD,
                                use_tls=settings.EMAIL_USE_TLS)
    return connection, settings.EMAIL_HOST_USER
