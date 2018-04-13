from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView

from apps.accounts import views
from apps.accounts.forms import CustomPasswordResetForm

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.DashboardView.as_view(), name='profile'),
    path('transaction-history/', views.TransactionHistoryView.as_view(), name='transaction-history'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings/', views.AccountSettings.as_view(), name='settings'),
    path('save-public-info/', views.PublicInfoSave.as_view(), name='save_public_info'),
    path('save-security-info/', views.SecurityInfoSave.as_view(), name='save_security_info'),
    path('save-ipn-settings/', views.IPNSettingsSave.as_view(), name='save_ipn_settings'),
    path('sign-up/', views.SignUpView.as_view(), name='signup'),
    path('sign-up-complete/', views.SignUpCompleteView.as_view(), name='signup_complete'),
    path('activate/<slug:key>', views.ProfileActivationView.as_view(), name='registration_activate'),
    path('password-reset', PasswordResetView.as_view(template_name='accounts/forgot_password.html',
                                                     form_class=CustomPasswordResetForm), name='reset_password'),

    path('create-2fa/', views.CreateTwoFactorAccount.as_view(), name='create_2fa'),
    path('2fa-list/', views.TwoFactorAccountList.as_view(), name='2fa_list'),
    path('delete-2fa/<int:pk>/', views.DeleteTwoFactorAccount.as_view(), name='delete_2fa'),

]
