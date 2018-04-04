from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView

from apps.store.models import StoreCategory


class StoreCategoryListView(ListView):
    model = StoreCategory
    queryset = StoreCategory.objects.filter(publish=True)
    context_object_name = 'categories'

