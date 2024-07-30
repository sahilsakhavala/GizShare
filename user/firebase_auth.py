from user.models import FirebaseAuth, User
from django.utils.translation import gettext_lazy as _


def firebase_auth(firebase, login_type):
    uid = firebase.uid
    provider_name = None
    email = None
    identifier = None
    name = None

    if firebase.provider_data and len(firebase.provider_data) > 0:
        provider = firebase.provider_data[0]
        provider_name = provider.provider_id
        email = provider.email
        identifier = provider.uid
        name = firebase.display_name

    if not provider_name or provider_name == 'phone':
        raise ValueError(_('Your requested provider is no valid for this request.'))

    try:
        firebase_auth = FirebaseAuth.objects.select_related('user').get(uid=uid)
        user = firebase_auth.user
    except FirebaseAuth.DoesNotExist as e:
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist as e:
                user = User.objects.create(email=email,
                                           name=name,
                                           login_type=login_type)
        else:
            user = User.objects.create(email=email,
                                       name=name,
                                       login_type=login_type)

        try:
            firebase_auth = FirebaseAuth.objects.get(user=user)
        except FirebaseAuth.DoesNotExist as e:
            firebase_auth = FirebaseAuth.objects.create(user=user,
                                                        uid=uid,
                                                        provider=provider_name,
                                                        identifier=identifier)

    return firebase_auth, user
