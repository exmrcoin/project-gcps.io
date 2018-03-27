from django.views.generic import TemplateView


class ReferanceView(TemplateView):
    template_name = 'common/index.html'

    def get_context_data(self, **kwargs):
        context = super(ReferanceView, self).get_context_data(**kwargs)
        key = kwargs.get('ref')
        print(key)


