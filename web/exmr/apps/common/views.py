from django.views.generic import TemplateView

from apps.accounts.models import Profile


class HomeView(TemplateView):
    template_name = 'common/index.html'

    def get_context_data(self, **kwargs):
        merchant_id = self.request.GET.get('ref')
        if merchant_id:
            user_profile = Profile.objects.get(merchant_id=merchant_id)
            referance_count = user_profile.referance_count
            referance_count = referance_count + 1
            user_profile.referance_count = referance_count
            user_profile.save()
        return super(HomeView, self).get_context_data(**kwargs)
