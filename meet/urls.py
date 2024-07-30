from django.urls import path
from . import views

urlpatterns = [
    path('meet-space/', views.MeetSpaceAPIView.as_view(), name='meet-space'),
    ]