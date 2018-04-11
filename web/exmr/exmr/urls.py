"""exmr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import patterns as patterns
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.views.i18n import set_language

from apps.common.views import HomeView
from apps.store.views import StoreCategoryListView, StoreCategoryDetailView

urlpatterns = [ path('admin/', admin.site.urls),
                path('rosetta/', include('rosetta.urls')),
                ]
urlpatterns += static( settings.STATIC_URL, document_root=settings.STATIC_ROOT )
urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )

urlpatterns += i18n_patterns(
    path('password-reset-done', PasswordResetDoneView.as_view(template_name='accounts/forgot_password_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('', include('apps.accounts.urls')),
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(template_name="accounts/login.html"), name='signin'),

    path('sign-up/', TemplateView.as_view(template_name='accounts/signup.html'),
         name='signup'),
    path('merchant-tools/', TemplateView.as_view(template_name='merchant-tools.html'), name='merchant-tools'),
    path('store-directory/', StoreCategoryListView.as_view(template_name='store-directory-menu.html'),
         name='store-directory'),
    path('store-directory/<slug:slug>', StoreCategoryDetailView.as_view(template_name='store-directory.html'), name='store-item'),

    path('forgot-password/', TemplateView.as_view(template_name='accounts/forgot-password.html'), name='forgot-password'),
)



