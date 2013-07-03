from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views.generic import TemplateView
from dsender import settings
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

    def post(self, request, *args, **kwargs):
        if not request.POST['mailing_list']:
            return redirect('start_mailing')

        mailing_list = request.POST['mailing_list']

        mailing = Mailing.objects.get(id=mailing_list)
        project = mailing.project
        email_list = project.email_list.all()

        settings.EMAIL_HOST = project.from_account.smtp_server
        for email in email_list:
            print("Sended to ", email.email)
            send_mail(subject=mailing.subject, message=mailing.text, from_email=project.from_account.smtp_user,
                      recipient_list=[email.email], fail_silently=False,
                      auth_user=project.from_account.smtp_user, auth_password=project.from_account.smtp_password)

        return redirect('start_mailing')