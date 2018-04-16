from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, TemplateView

from apps.accounts.models import Profile
from apps.store.forms import AddStoreForm
from apps.store.models import StoreCategory
from django.utils.translation import ugettext_lazy as _



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


class AddToStoreView(LoginRequiredMixin, CreateView):
    template_name = 'common/add-or-update.html'
    form_class = AddStoreForm
    success_url = reverse_lazy('store:addtostore_complete')


    def get_context_data(self, **kwargs):
        context = super(AddToStoreView, self).get_context_data(**kwargs)
        context['categories'] = StoreCategory.objects.filter(publish=True)
        return context


    def form_valid(self, form, commit=True):
        self.object = form.save(commit=False)
        username_or_merchant_id = form.cleaned_data['username_or_merch_id']
        try:
            user = User.objects.get(username=username_or_merchant_id)
            self.object.user = user

        except User.DoesNotExist:
            profile = Profile.objects.get(merchant_id=username_or_merchant_id)
            if profile:
                self.object.user = profile.user
        if commit:
            self.object.save()
            messages.add_message(self.request, messages.INFO,
                                 'Your store details has been added succesfully, '
                                 'We will review the details and get back to you soon')
            return super(AddToStoreView, self).form_valid(form)


class AddtoStoreComplete(TemplateView):
    template_name = 'common/message.html'
