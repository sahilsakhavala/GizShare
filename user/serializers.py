from rest_framework import serializers

from api.models import Post
from api.utils import validate_image
from .models import User, UserProfile, Currency, Language, Country, DeviceDetails, UserVerification
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from GizShare.email.send import EmailSender
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from notification.genrator import user_verification_notification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'gizer_subtype', 'gizer_name',
                  'speciality', 'organization_name', 'organization_type', 'organization_industry']


class UserProfileSerializer(serializers.ModelSerializer):
    picture = serializers.ImageField(validators=[validate_image], required=False, allow_empty_file=True)
    cover_picture = serializers.ImageField(validators=[validate_image], required=False, allow_empty_file=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'city', 'picture', 'cover_picture', 'bio', 'gender', 'country', 'currency', 'language',
                  'youtube_link',
                  'website_link', 'linkedin_link', 'twitter_link', 'facebook_link']


class AuthenticationSerializer(serializers.ModelSerializer):
    """This serializer for user authentication"""
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'token', 'phone_number']

    def get_token(self, instance):
        token = RefreshToken.for_user(instance).access_token
        return '{}'.format(token)


class AuthenticateSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'image', 'user_state', 'is_premium', 'last_login', 'date_joined', 'token']

    def get_token(self, object):
        return "{}".format(RefreshToken.for_user(object).access_token)


class DeviceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceDetails
        fields = ['id', 'type', 'device_id', 'model']


class FirebaseAuthSerializer(serializers.ModelSerializer):
    firebase = serializers.CharField(required=False, write_only=True)
    device_detail = DeviceDetailsSerializer(write_only=True)

    class Meta:
        model = User
        fields = ['firebase', 'device_detail', 'login_type']
    #
    # def validate_firebase(self, value):
    #     try:
    #         decoded_token = auth.verify_id_token(value)
    #         return auth.get_user(decoded_token['uid'])
    #     except exceptions.FirebaseError as ex:
    #         raise serializers.ValidationError("Firebase token is wrong. Error code: {}".format(ex.code))
    #     except Exception as e:
    #         raise serializers.ValidationError("Firebase token is wrong")
    #
    # def create(self, validated_data):
    #     try:
    #         device_detail = validated_data.pop('device_detail', None)
    #         print()
    #         firebase, user = firebase_auth(validated_data.pop('firebase'), validated_data['login_type'])
    #         inst, is_created = DeviceDetails.objects.get_or_create(
    #             user=user,
    #             defaults={
    #                 'type': device_detail['type'],
    #                 'device_id': device_detail['device_id'],
    #                 'model': device_detail['model'],
    #             }
    #         )
    #         if not user.is_active:
    #             error = {
    #                 "error": ["User account is blocked."]
    #             }
    #             raise serializers.ValidationError(error)
    #     except ValueError as e:
    #         raise serializers.ValidationError({
    #             "error": [_("Invalid token")],
    #             "details": [_(str(e))]
    #         })
    #
    #     firebase, user = firebase_auth(validated_data.pop("firebase"))
    #     if not user.is_active:
    #         raise serializers.ValidationError({
    #             "Error": "This Account is Not Active"
    #         })
    #     return user
    #
    # def to_representation(self, instance):
    #     user_logged_in.send(sender=type(instance), request=self.context['request'], user=instance)
    #     return AuthenticateSerializer(instance, context={'request': self.context['request']}).data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True,
                                     required=True, validators=[validate_password, ])
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)

    class Meta:
        model = User
        fields = ['user_type', 'username', 'email', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'password': _("Password field don't match")})
        password_validation.validate_password(data['password'], self.context['request'].user)
        return data

    def validate_password(self, value):
        try:
            password_validation.validate_password(value, self.instance)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            user_type=validated_data.get('user_type'),
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            password=validated_data.get('password')
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = ['username', 'password']


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'gizer_subtype', 'gizer_name',
                  'speciality', 'organization_name', 'organization_type', 'organization_industry', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        instance = super().update(instance, validated_data)
        if profile_data:
            UserProfile.objects.filter(user=instance).update(**profile_data)
        EmailSender.verify_email(self.context['request'], instance)
        return instance


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=200)


class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    confirm_password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationError({'token': [_('The reset link is invalid')]})

            user.set_password(password)
            user.save()

        except Exception as e:
            raise ValidationError({'token': [_('The reset link is invalid')]})
        return super().validate(attrs)


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'name']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name']


class CountrySerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(source='currency_set', many=True, read_only=True)
    language = LanguageSerializer(source='language_set', many=True, read_only=True)

    class Meta:
        model = Country
        fields = ['name', 'code', 'phone_code', 'currency', 'language']


class PostCountSerializer(serializers.ModelSerializer):
    period = serializers.CharField(read_only=True)
    post_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['period', 'post_count']


class UserVerificationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserVerification
        fields = ['id', 'user', 'passport', 'profile_picture', 'header_image', 'bio', 'letter']


class AdminUserVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVerification
        fields = ['status']

    def update(self, instance, validated_data):
        instance = super(AdminUserVerificationSerializer, self).update(instance, validated_data)
        user_verification_notification(instance)
        return instance