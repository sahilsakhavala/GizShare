from django.db.models import Prefetch
from api.models import Post
from .filters import UserProfileElasticSearchFilter
from .models import User, Currency, Language, Country, FirebaseAuth, UserProfile, UserVerification
from .serializers import (AuthenticationSerializer, RegisterSerializer, FirebaseAuthSerializer, LoginSerializer,
                          UserUpdateSerializer,
                          VerifyEmailSerializer,
                          RequestResetPasswordSerializer, SetNewPasswordSerializer, CountrySerializer,
                          CurrencySerializer, LanguageSerializer, UserSerializer, PostCountSerializer,
                          UserProfileSerializer, UserVerificationSerializer, AdminUserVerificationSerializer)
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from GizShare.email.send import EmailSender
from rest_framework.authentication import TokenAuthentication
from django_filters import rest_framework as filters
from django.db.models import Count
from django.db.models.functions import TruncYear, TruncMonth, TruncWeek, ExtractDay
from datetime import datetime


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    queryset = User.objects.all()


class FirebaseAuthView(generics.CreateAPIView):
    serializer_class = FirebaseAuthSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)
    queryset = FirebaseAuth.objects.all()


class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(username=serializer.data.get("username"))
            data = AuthenticationSerializer(user, context={"request": self.request}).data
            if not user.check_password(request.data["password"]):
                error = {'password': [_("Invalid username or password.")]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            # elif not user.verified:
            #     error = {'phone_number': [_("Your account has not been verified. Please verify your email to log in.")]}
            #     return Response(error, status=status.HTTP_400_BAD_REQUEST)
            elif not user.is_active:
                error = {'username': [
                    _("Username Already Registered but account deactivated, please contact support team for Account recovery.")]}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Login successfully', 'data': data}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            error = {'username': [_("Invalid username or password.")]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [UserProfileElasticSearchFilter]
    queryset = UserProfile.objects.all()


class UpdateUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_classes = {
        'PATCH': UserUpdateSerializer,
        'PUT': UserUpdateSerializer,
        'GET': UserUpdateSerializer
    }
    permission_classes = [IsAuthenticated, ]
    lookup_field = 'id'

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        return self.serializer_classes.get(self.request.method)


class VerifyEmailView(APIView):
    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]

    def get(self, request, uid_base64, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uid_base64)
            uid = force_bytes(uid)
            user = User.objects.get(pk=uid)
        except User.DoesNotExists:
            user = None
        if user is not None:
            user.verified = True
            user.save(update_fields=['verified'])
            return Response({'detail': 'Email verified successfully'}, status=200)
        else:
            return Response({'detail': 'Invalid verification link'}, status=400)


class RequestResetPasswordView(APIView):
    serializer_class = RequestResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'email': [_('No user found with this email address.')]}, status=status.HTTP_404_NOT_FOUND)

        if not user.verified:
            EmailSender.verify_email(request, user)
            return Response(
                {'email': [_('You are not Verify, Verification email has been sent. Please check your mail.')]},
                status=status.HTTP_200_OK)
        else:
            EmailSender.reset_password_request_mail(request, user)
            return Response({'email': [
                _('Reset password link has been sent to your registered email. Please check your inbox or spam folder.')]},
                status=status.HTTP_200_OK)


class SetNewPasswordView(APIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': [_('Password reset done')]}, status=status.HTTP_200_OK)


class CountryDetailView(generics.ListAPIView):
    serializer_class = CountrySerializer

    def get_queryset(self):
        return Country.objects.prefetch_related(
            Prefetch('language_set', queryset=Language.objects.all()),
            Prefetch('currency_set', queryset=Currency.objects.all()),
        )


class CurrencyView(generics.ListAPIView):
    serializer_class = CurrencySerializer
    queryset = Currency.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['country']


class LanguageView(generics.ListAPIView):
    serializer_class = LanguageSerializer
    queryset = Language.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['country']


class UserGraphView(APIView):
    def get(self, request, *args, **kwargs):
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = User.objects.filter(is_active=False).count()
        data = {
            'labels': ['Active Users', 'Inactive Users'],
            'default': [active_users, inactive_users],
        }
        return Response(data)


class PostGraphView(APIView):
    serializer_class = PostCountSerializer

    def get(self, request):
        period = request.query_params.get('period')
        data = {}

        if period == 'monthly':
            current_year = datetime.now().year
            post_qs = Post.objects.filter(user__is_active=True, created_at__year=current_year) \
                .annotate(period=TruncMonth('created_at')) \
                .values('period') \
                .annotate(post_count=Count('id'))
            data['post_labels'] = [entry['period'].strftime('%B') for entry in post_qs]
            data['post_counts'] = [entry['post_count'] for entry in post_qs]

        elif period == 'yearly':
            post_qs = Post.objects.filter(user__is_active=True) \
                .annotate(period=TruncYear('created_at')) \
                .values('period') \
                .annotate(post_count=Count('id'))
            data['post_labels'] = [entry['period'].strftime('%Y') for entry in post_qs]
            data['post_counts'] = [entry['post_count'] for entry in post_qs]

        elif period == 'weekly':
            current_year = datetime.now().year
            current_month = datetime.now().month

            post_qs = Post.objects.filter(user__is_active=True, created_at__year=current_year,
                                          created_at__month=current_month) \
                .annotate(week=TruncWeek('created_at'), day_of_week=ExtractDay('created_at')) \
                .values('week', 'day_of_week') \
                .annotate(post_count=Count('id')) \
                .order_by('week', 'day_of_week')

            weeks = {}
            for entry in post_qs:
                week_start = entry['week'].strftime('%Y-%m-%d')
                day_of_week = entry['day_of_week']
                if week_start not in weeks:
                    weeks[week_start] = [0] * 7
                weeks[week_start][day_of_week - 1] = entry['post_count']

            data['post_labels'] = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            data['post_counts'] = [weeks[week] for week in sorted(weeks.keys())]

        return Response(data)


class UserVerificationView(generics.ListCreateAPIView):
    serializer_class = UserVerificationSerializer

    def get_queryset(self):
        return UserVerification.objects.filter(user=self.request.user)


class AdminUserVerificationView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminUserVerificationSerializer
    permission_classes = [IsAdminUser]
    queryset = UserVerification.objects.all()
    lookup_field = 'id'
