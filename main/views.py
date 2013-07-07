from django.conf import settings as global_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.core.context_processors import csrf
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext as _
from smtplib import SMTPException
from dsender.functions import prepare_data
from main.models import Message, Project, Group, MailAccount, Log, Client


@login_required
@require_http_methods(["GET"])
def page_home(request):
    data = prepare_data(request)

    return render(request, "pages/page_home.html", {
        'title': _("Main page"),
        'data': data,
    })


@login_required
@require_http_methods(["GET"])
def page_select_project(request):
    data = prepare_data(request)
    projects = Project.objects.all()

    content = {
        'projects': projects,
    }

    return render(request, "pages/page_select_project.html", {
        'title': _("Select project") + " - 1/4",
        'data': data,
        'content': content
    })


@login_required
@require_http_methods(["GET"])
def page_select_group(request):
    if 'project' not in request.GET:
        messages.error(request, _("Project not selected"))
        return redirect('select_project')

    try:
        project = Project.objects.get(id=request.GET['project'])
    except Project.DoesNotExist as error_message:
        messages.error(request, error_message)
        return redirect('select_project')

    data = prepare_data(request)
    groups = Group.objects.filter(project=project)

    content = {
        'groups': groups,
        'project': project,
    }

    return render(request, "pages/page_select_group.html", {
        'title': _("Select group") + " - 2/4",
        'data': data,
        'content': content
    })


@login_required
@require_http_methods(["GET"])
def page_select_message(request):
    if 'group' not in request.GET:
        messages.error(request, _("Group not selected"))
        return redirect('select_group')

    try:
        group = Group.objects.get(id=request.GET['group'])
    except Project.DoesNotExist as error_message:
        messages.error(request, error_message)
        return redirect('select_group')

    data = prepare_data(request)
    mail_messages = Message.objects.filter(group=group)

    content = {
        'group': group,
        'mail_messages': mail_messages,
        'project': group.project,
        'to_emails': group.clients.all()
    }

    return render(request, "pages/page_select_message.html", {
        'title': _("Select message") + " - 3/4",
        'data': data,
        'content': content
    })


@csrf_protect
@login_required
@require_http_methods(["GET"])
def page_confirm(request):
    if 'message' not in request.GET:
        messages.error(request, _("Message not selected"))
        return redirect('select_message')

    try:
        message = Message.objects.get(id=request.GET['message'])
    except Project.DoesNotExist as error_message:
        messages.error(request, error_message)
        return redirect('select_group')

    c = {}
    c.update(csrf(request))
    data = prepare_data(request)

    content = {
        'mail_message': message,
        'project': message.group.project,
        'group': message.group,
        'to_emails': message.group.clients.all()
    }

    return render(request, "pages/page_confirm.html", {
        'title': _("Confirm") + " - 4/4",
        'data': data,
        'content': content
    })


@csrf_protect
@login_required
@require_http_methods(["POST"])
def page_send(request):
    if 'message' not in request.POST:
        messages.error(request, _("Message not selected"))
        return redirect('select_message')

    c = {}
    c.update(csrf(request))

    try:
        mail_message = Message.objects.get(id=int(request.POST['message']))
    except Message.DoesNotExist as error_message:
        messages.error(request, error_message)
        return redirect('select_message')

    group = mail_message.group
    project = group.project
    clients = group.clients.all()

    global_settings.EMAIL_HOST = project.from_account.server
    global_settings.EMAIL_HOST_USER = project.from_account.username
    global_settings.EMAIL_HOST_PASSWORD = project.from_account.password
    global_settings.EMAIL_PORT = project.from_account.port
    global_settings.EMAIL_USE_TLS = project.from_account.use_tls

    try:
        connection = mail.get_connection()
        connection.open()
    except SMTPException as error_message:
        messages.error(request, error_message)
        return redirect('home')

    email_message_array = []
    if group.mailing_type == 0:
        emails_array = []
        for client in clients:
            emails_array.append(client.email)
            Log.objects.create(action=0, user=request.user, from_account=project.from_account, from_project=project,
                               from_group=group, message=mail_message, client=client)

        msg = mail.EmailMessage(mail_message.subject, mail_message.text, project.from_account.username, emails_array)
        msg.content_subtype = mail_message.content_type
        email_message_array.append(msg)
    elif group.mailing_type == 1:
        for client in clients:
            msg = mail.EmailMessage(mail_message.subject, mail_message.text, project.from_account.username,
                                    [client.email])
            msg.content_subtype = mail_message.content_type
            email_message_array.append(msg)
            Log.objects.create(action=0, user=request.user, from_account=project.from_account, from_project=project,
                               from_group=group, message=mail_message, client=client)

    try:
        messages_count = connection.send_messages(email_message_array)
    except SMTPException as error_message:
        messages.error(request, error_message)
        return redirect('home')

    # %-)
    try:
        mail_account = MailAccount.objects.get(id=project.from_account.id)
    except MailAccount.DoesNotExist as error_message:
        messages.error(request, "WTF?! " + error_message)
        return redirect('home')

    mail_account.counter += messages_count
    mail_account.save()

    connection.close()

    messages.success(request, _("Successful"))
    return redirect('home')


@csrf_protect
@login_required
@require_http_methods(["GET"])
def page_logs(request):
    data = prepare_data(request)

    content = {
        'logs': Log.objects.all()
    }

    return render(request, "pages/page_logs_view.html", {
        'title': _("View all logs"),
        'data': data,
        'content': content,
    })


@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def page_client_add(request):
    data = prepare_data(request)

    return render(request, "pages/page_client_add.html", {
        'title': _("Add new client"),
        'data': data,
    })


@csrf_protect
@login_required
@require_http_methods(["GET"])
def page_client_view(request, client_id):
    data = prepare_data(request)

    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist as error_message:
        messages.error(request, error_message)
        return redirect('home')

    content = {
        'client': client,
        'groups': Group.objects.filter(clients__in=client_id),
    }

    return render(request, "pages/page_client_view.html", {
        'title': _("View client"),
        'data': data,
        'content': content,
    })