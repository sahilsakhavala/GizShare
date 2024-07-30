from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_image(value):
    filesize = value.size

    if filesize > 10 * 1024 * 1024:
        raise ValidationError(_('The maximum file size of file is 10MB'))
