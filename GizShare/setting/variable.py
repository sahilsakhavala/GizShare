import os
from django.conf import settings

FIREBASE_DIR = os.path.join(os.path.dirname(settings.BASE_DIR), "config/firebase.json")

CURRENT_SITE = os.environ.get('CURRENT_SITE')
