from django.views.generic import TemplateView
from main.models import Project, Mailing


class Home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['title'] = "Home"
        return context


class StartMailing(TemplateView):
    template_name = "start_mailing.html"

    def get_context_data(self, **kwargs):
        context = super(StartMailing, self).get_context_data(**kwargs)
        context['mailing_lists'] = Mailing.objects.all()[:10]
        context['title'] = "Start Mailing"
        return context