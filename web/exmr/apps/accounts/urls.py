from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('profile/', TemplateView.as_view(template_name="accounts/profile.html")),

]