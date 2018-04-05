from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView

from apps.store.models import StoreCategory


class StoreCategoryListView(ListView):
    model = StoreCategory
    queryset = StoreCategory.objects.filter(publish=True)
    context_object_name = 'categories'



class StoreCategoryDetailView(DetailView):
    model = StoreCategory
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super(StoreCategoryDetailView, self).get_context_data(**kwargs)
        context['categories'] = StoreCategory.objects.filter(publish=True)
        return context

