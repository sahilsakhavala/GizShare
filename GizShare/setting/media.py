import os
from pathlib import Path

from GizShare.setting.funtion import get_bool
from GizShare.settings import BASE_DIR

if get_bool('USE_S3', False):
    # TODO START S3 object storage
    DEFAULT_FILE_STORAGE = 'pbsm.storage_backend.PublicMediaStorage'
    STATICFILES_STORAGE = 'pbsm.storage_backend.StaticStorage'

    AWS_STATIC_LOCATION = os.environ.get('STATIC_LOCATION')
    AWS_MEDIA_LOCATION = os.environ.get('MEDIA_LOCATION')
    AWS_S3_REGION_NAME = os.environ.get('S3_REGION_NAME')
    AWS_ACCESS_KEY_ID = os.environ.get('ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('STORAGE_BUCKET_NAME')
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False

    STATIC_URL = f'/{AWS_STATIC_LOCATION}/'
    MEDIA_URL = f'/{AWS_MEDIA_LOCATION}/'


else:
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'

    STATIC_ROOT = Path(BASE_DIR, 'static_cdn')
    MEDIA_ROOT = Path(BASE_DIR, 'media_cdn')
