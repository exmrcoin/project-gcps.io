from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from apps.accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('sign-up/', views.SignUpView.as_view(), name='signup'),
    path('sign-up-complete/', views.SignUpCompleteView.as_view(), name='signup_complete'),
    path('activate/<slug:key>', views.ProfileActivationView.as_view(), name='registration_activate'),
]
