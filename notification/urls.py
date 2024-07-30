from django.urls import path
from . import views

urlpatterns = [
    path('notification/', views.NotiFicationView.as_view(), name='notification'),
]
