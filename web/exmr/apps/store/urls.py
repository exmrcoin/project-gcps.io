from django.urls import path

from apps.store import views

app_name = 'store'

urlpatterns = [
    path('add-to-store/', views.AddToStoreView.as_view(), name='add-to-store'),
    ]