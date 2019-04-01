from django.urls import path

from apps.store import views
from apps.store.views import StoreCategoryListView, StoreListView, StoreCheckout,\
                             PaymentFormSubmitView, StoreRateView, StoreUpdate

app_name = 'store'

urlpatterns = [
    path('<int:pk>/update-store/', views.StoreUpdate.as_view(), name='update-store'),
    path('add-to-store/', views.AddToStoreView.as_view(), name='add-to-store'),
    path('add-to-store-complete/', views.AddtoStoreComplete.as_view(), name='addtostore_complete'),
    path('store-directory/<slug:slug>/', StoreListView.as_view(), name='store-item'),
    path('store-directory/<slug:slug>/rate/<int:pk>/', StoreRateView.as_view(), name='store-item-rate'),
    path('store-directory/<slug:slug>/rate/<int:pk>/vote/', views.StoreVote.as_view(), name='store-vote'),
    # path('store-directory/<slug:slug>/rate/<int:pk>/vote/', vote, name='store-vote'),
    path('store-directory/', StoreCategoryListView.as_view(), name='store-directory'),
    path('stores/', StoreListView.as_view(), name='store-search'),
    path('check-out/<int:pk>/', StoreCheckout.as_view(), name='check-out'),
    path('payment-process-1/', PaymentFormSubmitView.as_view(),  name='payprocess'),

]