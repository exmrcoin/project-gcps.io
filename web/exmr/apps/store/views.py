import operator
from functools import reduce

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, TemplateView

from apps.accounts.decorators import ckeck_2fa
from apps.accounts.models import Profile
from apps.store.forms import AddStoreForm
from apps.store.models import StoreCategory, Store


class StoreCategoryListView(ListView):

    template_name = 'store/store_categories.html'
    model = StoreCategory
    queryset = StoreCategory.objects.filter(publish=True)
    context_object_name = 'categories'


class StoreListView(ListView):
    template_name = 'store/store_listing.html'
    model = Store
    context_object_name = 'stores'

    def get_context_data(self,*args,**kwargs):
        q = self.request.GET.get('q')
        slug = self.kwargs.get('slug')
        context = super(StoreListView, self).get_context_data(**kwargs)
        if slug:
            self.category = get_object_or_404(StoreCategory, slug=slug)
            context['category'] = self.category
        elif q:
            context['stores'] = Store.objects.filter(Q(store_name__icontains=q) | Q(category__name__icontains=q))
        context['categories'] = StoreCategory.objects.filter(publish=True)
        return context

@method_decorator(ckeck_2fa, name='dispatch')
class AddToStoreView(LoginRequiredMixin, CreateView):
    template_name = 'store/add-or-update.html'
    form_class = AddStoreForm
    success_url = reverse_lazy('store:addtostore_complete')

    def get_context_data(self, **kwargs):
        context = super(AddToStoreView, self).get_context_data(**kwargs)
        context['categories'] = StoreCategory.objects.filter(publish=True)
        return context

    def form_valid(self, form, commit=True):
        self.object = form.save(commit=False)
        username_or_merchant_id = form.cleaned_data['username_or_merch_id']
        if Profile.objects.filter(merchant_id=username_or_merchant_id).exists():
            profile = Profile.objects.get(merchant_id=username_or_merchant_id)
        elif Profile.objects.filter(user__username=username_or_merchant_id).exists():
            profile = Profile.objects.get(user__username=username_or_merchant_id)

        self.object.user = profile.user
        if commit:
            self.object.save()
            messages.add_message(self.request, messages.INFO,
                                 'Your store details has been added successfully, '
                                 'We will review the details and get back to you soon')
            return super(AddToStoreView, self).form_valid(form)


class AddtoStoreComplete(TemplateView):
    template_name = 'common/message.html'



