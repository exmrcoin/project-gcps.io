from django.urls import path

from apps.store import views

app_name = 'store'

urlpatterns = [
    path('add-to-store/', views.AddToStoreView.as_view(), name='add-to-store'),
    path('add-to-store-complete/', views.AddtoStoreComplete.as_view(), name='addtostore_complete'),
]