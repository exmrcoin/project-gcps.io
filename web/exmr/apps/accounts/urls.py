from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView

from apps.accounts import views
from apps.accounts.forms import CustomPasswordResetForm
from apps.accounts.views import  AccountSettings

app_name = 'accounts'

urlpatterns = [
    # path('profile/', login_required(TemplateView.as_view(template_name="accounts/dashboard.html")), name='profile'),
    path('profile/', views.DashboardView.as_view(), name='profile'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings/', AccountSettings.as_view(), name='settings'),
    path('sign-up/', views.SignUpView.as_view(), name='signup'),
    path('sign-up-complete/', views.SignUpCompleteView.as_view(), name='signup_complete'),
    path('activate/<slug:key>', views.ProfileActivationView.as_view(), name='registration_activate'),
    path('password-reset', PasswordResetView.as_view(template_name='accounts/forgot_password.html',
                                                     form_class=CustomPasswordResetForm), name='reset_password'),

]
