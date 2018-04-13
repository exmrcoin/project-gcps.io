from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView

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
    success_url = reverse_lazy('store:add-to-store')

    def get_initial(self):
        initial = super(AddToStoreView, self).get_initial()
        initial['merchant_id'] = self.request.user.get_profile.merchant_id
        return initial


    def get_context_data(self, **kwargs):
        context = super(AddToStoreView, self).get_context_data(**kwargs)
        context['categories'] = StoreCategory.objects.filter(publish=True)
        profile = Profile.objects.get(user=self.request.user)
        context['merchant_id'] = profile.merchant_id
        return context

    def form_valid(self, form):
        form.save(commit=True)
        print(form.cleaned_data)
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))
