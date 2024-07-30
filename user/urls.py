from django.urls import path
from . import views

urlpatterns = [
    path('firebase/login/', views.FirebaseAuthView.as_view(), name='firebase-auth'),
    path('register/', views.RegisterView.as_view(), name='user-register'),
    path('login/', views.LoginView.as_view(), name='user-login'),
    path('user/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('user/<int:id>/', views.UpdateUserView.as_view(), name='user'),
    path('verify_email/<uid_base64>/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('request_reset_password/', views.RequestResetPasswordView.as_view(), name='request-reset-password'),
    path('reset_password/<uidb64>/<token>/', views.SetNewPasswordView.as_view(), name='reset-password-confirm'),
    path('country/', views.CountryDetailView.as_view(), name='country'),
    path('currency/', views.CurrencyView.as_view(), name='currency'),
    path('language/', views.LanguageView.as_view(), name='language'),
    path('active-users/', views.UserGraphView.as_view(), name='active-users'),
    path('post-graph-data/', views.PostGraphView.as_view(), name='post-graph-data'),
    path('user-verification/', views.UserVerificationView.as_view(), name='user-verification'),
    path('admin/user-verification/<int:id>/', views.AdminUserVerificationView.as_view(), name='admin_user_verification'),
]
