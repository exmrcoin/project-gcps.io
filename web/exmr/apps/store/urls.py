from django.urls import path

from apps.store import views
from apps.store.views import StoreCategoryListView, StoreListView, StoreCheckout,\
                             PaymentFormSubmitView

app_name = 'store'

urlpatterns = [
    path('add-to-store/', views.AddToStoreView.as_view(), name='add-to-store'),
    path('add-to-store-complete/', views.AddtoStoreComplete.as_view(), name='addtostore_complete'),
    path('store-directory/<slug:slug>/', StoreListView.as_view(), name='store-item'),
    path('store-directory/', StoreCategoryListView.as_view(), name='store-directory'),
    path('stores/', StoreListView.as_view(), name='store-search'),
    path('check-out/<int:pk>/', StoreCheckout.as_view(), name='check-out'),
    path('payment-process-1/', PaymentFormSubmitView.as_view(),  name='payprocess'),

]