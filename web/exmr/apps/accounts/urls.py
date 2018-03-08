from django.urls import path

from Website.exmr.apps.accounts import views

urlpatterns = [
    path('register/', views.SignUp.as_view(), name='register'),
]