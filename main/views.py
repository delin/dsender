from django.conf import settings as global_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf, request
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _
from dsender.functions import prepare_data
from main.models import Mailing, Project


class Home(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['title'] = _("Main page")
        return context


class StartMailing(TemplateView):
    template_name = "pages/start_mailing.html"

    c = {}
    c.update(csrf(request))

    # def get(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated():
    #         return redirect('login')

    def get_context_data(self, **kwargs):
        context = super(StartMailing, self).get_context_data(**kwargs)
        context['mailing_lists'] = Mailing.objects.all()[:10]
        context['title'] = _("Start mailing")
        return context

    def post(self, request, *args, **kwargs):
        if not request.POST['mailing_list']:
            return redirect('start_mailing')

        mailing_list = request.POST['mailing_list']

        mailing = Mailing.objects.get(id=mailing_list)
        project = mailing.project
        email_list = project.email_list.all()

        global_settings.EMAIL_HOST = project.from_account.server
        global_settings.EMAIL_HOST_USER = project.from_account.username
        global_settings.EMAIL_HOST_PASSWORD = project.from_account.password
        global_settings.EMAIL_PORT = project.from_account.port
        global_settings.EMAIL_USE_TLS = project.from_account.use_tls

        for email in email_list:
            send_mail(subject=mailing.subject,
                      message=mailing.text,
                      from_email=project.from_account.username,
                      recipient_list=[email.email],
                      fail_silently=False)

        return redirect('start_mailing')


@login_required
@require_http_methods(["GET"])
def page_select_project(request):
    title = _("Select project") + " - 1/3"

    data = prepare_data(request)
    projects = Project.objects.all()

    content = {
        'projects': projects,
    }

    return render(request, "pages/select_project.html", {
        'data': data,
        'title': title,
        'content': content
    })


@login_required
@require_http_methods(["GET"])
def page_select_message(request):
    if 'project' not in request.GET:
        messages.error(request, _("Project not selected"))
        return redirect('select_project')

    title = _("Select message") + " - 2/3"

    data = prepare_data(request)
    mail_messages = Mailing.objects.filter(project=request.GET['project'])

    content = {
        'mail_messages': mail_messages,
    }

    return render(request, "pages/select_message.html", {
        'data': data,
        'title': title,
        'content': content
    })


@login_required
@require_http_methods(["GET"])
def page_confirm(request):
    if 'message' not in request.GET:
        messages.error(request, _("Message not selected"))
        return redirect('select_message')

    title = _("Confirm") + " - 3/3"

    data = prepare_data(request)

    try:
        mail_message = Mailing.objects.get(id=int(request.GET['message']))
    except Mailing.DoesNotExist as error_message:
        messages.error(request, error_message)
        return redirect('select_message')

    content = {
        'mail_message': mail_message,
        'to_emails': mail_message.project.email_list.all()
    }

    return render(request, "pages/confirm.html", {
        'data': data,
        'title': title,
        'content': content
    })


@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def page_send(request):
    title = _("Sending")
    data = prepare_data(request)

    c = {}
    c.update(csrf(request))

    if request.method == "POST":
        if 'message' not in request.POST:
            messages.error(request, _("Message not selected"))
            return redirect('select_message')

        try:
            mail_message = Mailing.objects.get(id=int(request.POST['message']))
        except Mailing.DoesNotExist as error_message:
            messages.error(request, error_message)
            return redirect('select_message')

        project = mail_message.project
        email_list = project.email_list.all()

        global_settings.EMAIL_HOST = project.from_account.server
        global_settings.EMAIL_HOST_USER = project.from_account.username
        global_settings.EMAIL_HOST_PASSWORD = project.from_account.password
        global_settings.EMAIL_PORT = project.from_account.port
        global_settings.EMAIL_USE_TLS = project.from_account.use_tls

        for email in email_list:
            send_mail(subject=mail_message.subject,
                      message=mail_message.text,
                      from_email=project.from_account.username,
                      recipient_list=[email.email],
                      fail_silently=False)

        messages.success(request, _("Successful"))
        return redirect('start_mailing')

    # return render(request, "pages/confirm.html", {
    #     'data': data,
    #     'title': title,
    #     'content': content
    # })