from datetime import datetime
from hashlib import md5
from django.conf import settings as global_settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.sites.models import get_current_site
from django.core import mail
from django.core.context_processors import csrf
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.shortcuts import redirect, render
from django.template import Context
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext as _
from smtplib import SMTPException
from random import randint
from dsender.functions import prepare_data
from dsender.settings import DEBUG
from main.forms import ClientForm, ProjectForm, GroupForm, MessageForm
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

    if projects.count() == 0:
        messages.warning(request, _("The project list is empty."))
        return redirect(page_project_add)

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

    if groups.count() == 0:
        messages.warning(request, _("The group list is empty."))
        return redirect(page_group_add)

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

    clients = group.clients.filter(is_removed=False, is_unsubscribed=False).all()
    if not clients:
        messages.warning(request, _("Group not selected."))
        return redirect('select_group')

    data = prepare_data(request)
    mail_messages = Message.objects.filter(group=group)

    if mail_messages.count() == 0:
        messages.warning(request, _("The mailing list is empty."))
        return redirect(page_message_add)

    content = {
        'group': group,
        'mail_messages': mail_messages,
        'project': group.project,
        'to_emails': clients
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

    clients = message.group.clients.filter(is_removed=False, is_unsubscribed=False).all()
    if not clients:
        messages.warning(request, _("The mailing list is empty."))
        return redirect('select_group')

    c = {}
    c.update(csrf(request))
    data = prepare_data(request)

    message_plain = get_template('messages/base.txt')
    message_html = get_template('messages/base.html')

    message_content = Context({
        'message': message.text,
    })

    if message.content_type == "html":
        message_text = message_html.render(message_content)
    else:
        message_text = message_plain.render(message_content)

    content = {
        'mail_message': message,
        'project': message.group.project,
        'group': message.group,
        'to_emails': clients,
        'message_text': message_text,
    }

    return render(request, "pages/page_confirm.html", {
        'title': _("Confirm") + " - 4/4",
        'data': data,
        'content': content,
        'clients': clients,
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
    clients = group.clients.filter(is_removed=False, is_unsubscribed=False)

    global_settings.EMAIL_HOST = project.from_account.server
    global_settings.EMAIL_HOST_USER = project.from_account.username
    global_settings.EMAIL_HOST_PASSWORD = project.from_account.password
    global_settings.EMAIL_PORT = project.from_account.port
    global_settings.EMAIL_USE_TLS = project.from_account.use_tls

    messages_count = 0
    if group.mailing_type == 0:         # as Copy
        try:
            connection = mail.get_connection()
            connection.open()
        except SMTPException as error_message:
            messages.error(request, error_message)
            return redirect('home')

        emails_array = []
        for client in clients:
            emails_array.append(client.email)
            client.last_send = datetime.now()
            client.save()
            Log.objects.create(action=0, user=request.user, from_account=project.from_account, from_project=project,
                               from_group=group, message=mail_message, client=client)

        msg = mail.EmailMessage(mail_message.subject, mail_message.text, project.from_account.username, emails_array)
        msg.content_subtype = mail_message.content_type

        try:
            messages_count = connection.send_messages(msg)
            connection.close()
        except SMTPException as error_message:
            messages.error(request, error_message)
            return redirect('home')
    elif group.mailing_type == 1:       # as Private
        message_plain = get_template('messages/base.txt')
        message_html = get_template('messages/base.html')

        for client in clients:
            if 'button_send_test' in request.POST:
                client = request.user

            content = Context({
                'client': client,
                'message': mail_message.text,
                'site': get_current_site(request),
            })

            if mail_message.content_type == "html":
                message = message_html.render(content)
            else:
                message = message_plain.render(content)

            try:
                msg = EmailMessage(mail_message.subject, message, project.from_account.username, [client.email])
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
            except SMTPException as error_message:
                messages.error(request, error_message)
                return redirect('home')

            if 'button_send_test' in request.POST:
                Log.objects.create(action=8, user=request.user, from_account=project.from_account, from_project=project,
                                   from_group=group, message=mail_message)
                break
            else:
                client.last_send = datetime.now()
                client.save()
                Log.objects.create(action=0, user=request.user, from_account=project.from_account, from_project=project,
                                   from_group=group, message=mail_message, client=client)
            messages_count += 1

    try:
        mail_account = MailAccount.objects.get(id=project.from_account.id)
    except MailAccount.DoesNotExist as error_message:
        messages.error(request, "WTF?! " + error_message)
        return redirect('home')

    mail_account.counter += messages_count
    mail_account.save()

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
@require_http_methods(["GET"])
def page_project_list(request):
    data = prepare_data(request)

    content = {
        'projects': Project.objects.filter(is_removed=False)
    }

    return render(request, "pages/page_project_list.html", {
        'title': _("Projects list"),
        'data': data,
        'content': content,
    })


@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def page_project_add(request):
    data = prepare_data(request)

    project_form = ProjectForm(request.POST or None)
    if request.method == "POST":
        if project_form.is_valid():
            new_project = project_form.save()

            Log.objects.create(action=5, user=request.user, from_project=new_project,
                               from_account=new_project.from_account)

            messages.success(request, _("Created"))
            return redirect('project_add')
        else:
            messages.error(request, project_form.errors)

    content = {
        'form': project_form,
    }

    return render(request, "pages/page_project_add.html", {
        'title': _("Add new project"),
        'data': data,
        'content': content,
    })


@csrf_protect
@login_required
@require_http_methods(["GET"])
def page_project_view(request, project_id):
    data = prepare_data(request)

    try:
        project = Project.objects.get(id=project_id, is_removed=False)
    except Project.DoesNotExist as error_message:
        messages.error(request, error_message)
        return redirect('home')

    content = {
        'project': project,
        'logs': Log.objects.filter(from_project=project),
    }

    return render(request, "pages/page_project_view.html", {
        'title': _("View project"),
        'data': data,
        'content': content,
    })


@csrf_protect
@login_required
@require_http_methods(["GET"])
def page_group_list(request):
    data = prepare_data(request)

    content = {
        'groups': Group.objects.filter(is_removed=False)
    }

    return render(request, "pages/page_group_list.html", {
        'title': _("Groups list"),
        'data': data,
        'content': content,
    })


@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def page_group_add(request):
    data = prepare_data(request)

    clients_count = Client.objects.count()
    if clients_count == 0:
        messages.warning(request, _("The clients list is empty."))
        return redirect(page_client_add)

    group_form = GroupForm(request.POST or None)
    if request.method == "POST":
        if group_form.is_valid():
            new_group = group_form.save()

            Log.objects.create(action=12, user=request.user, from_group=new_group, from_project=new_group.project,
                               from_account=new_group.project.from_account)

            messages.success(request, _("Created"))
            return redirect('group_add')
        else:
            messages.error(request, group_form.errors)

    content = {
        'form': group_form,
    }

    return render(request, "pages/page_group_add.html", {
        'title': _("Add new group"),
        'data': data,
        'content': content,
    })


@csrf_protect
@login_required
@require_http_methods(["GET"])
def page_group_view(request, group_id):
    data = prepare_data(request)

    try:
        group = Group.objects.get(id=group_id, is_removed=False)
    except Project.DoesNotExist as error_message:
        messages.error(request, error_message)
        return redirect('home')

    content = {
        'group': group,
        'clients': group.clients.all(),
        'logs': Log.objects.filter(from_group=group),
    }

    return render(request, "pages/page_group_view.html", {
        'title': _("View group"),
        'data': data,
        'content': content,
    })


@csrf_protect
@login_required
@require_http_methods(["GET"])
def page_message_list(request):
    data = prepare_data(request)

    content = {
        'messages': Message.objects.filter(is_removed=False)
    }

    return render(request, "pages/page_message_list.html", {
        'title': _("Messages list"),
        'data': data,
        'content': content,
    })


@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def page_message_add(request):
    data = prepare_data(request)

    message_form = MessageForm(request.POST or None)
    if request.method == "POST":
        if message_form.is_valid():
            new_message = message_form.save()

            Log.objects.create(action=6, user=request.user, message=new_message, from_project=new_message.group.project,
                               from_group=new_message.group, from_account=new_message.group.project.from_account)

            messages.success(request, _("Created"))
            return redirect('message_add')
        else:
            messages.error(request, message_form.errors)

    content = {
        'form': message_form,
    }

    return render(request, "pages/page_message_add.html", {
        'title': _("Add new message"),
        'data': data,
        'content': content,
    })


@csrf_protect
@login_required
@require_http_methods(["GET"])
def page_client_list(request):
    data = prepare_data(request)

    content = {
        'clients': Client.objects.filter(is_removed=False)
    }

    return render(request, "pages/page_client_list.html", {
        'title': _("Clients list"),
        'data': data,
        'content': content,
    })


@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def page_client_add(request):
    data = prepare_data(request)

    client_form = ClientForm(request.POST or None)
    if request.method == "POST":
        if client_form.is_valid():
            new_client = client_form.save(commit=False)
            new_client.unsubscribe_code = md5(
                str(request.POST['email'] + str(randint(100000, 1000000))).encode()).hexdigest()
            new_client.save()

            Log.objects.create(action=7, user=request.user, client=new_client)

            messages.success(request, _("Created"))
            return redirect('client_add')
        else:
            messages.error(request, client_form.errors)

    content = {
        'client_form': client_form,
    }

    return render(request, "pages/page_client_add.html", {
        'title': _("Add new client"),
        'data': data,
        'content': content,
    })


@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def page_client_mass_add(request):
    data = prepare_data(request)

    if request.method == "POST":
        if 'emails_list' in request.POST:
            emails = request.POST['emails_list']
            emails_array = emails.splitlines()
            emails_add = 0
            emails_error = 0
            emails_exist = 0
            for email in emails_array:
                if len(email) >= 3:
                    # try:
                    #     is_valid = validate_email(email, verify=True)
                    # except BaseException as e:
                    #     if DEBUG:
                    #         messages.warning(request, e)
                    #     return redirect(page_client_mass_add)

                    # if is_valid:
                        check_client = Client.objects.filter(email=email).count()
                        if check_client == 0:
                            code = md5(str(email + str(randint(100000, 1000000))).encode()).hexdigest()
                            new_client = Client.objects.create(email=email, unsubscribe_code=code)
                            Log.objects.create(action=7, user=request.user, client=new_client)
                            emails_add += 1
                        else:
                            # messages.info(request, str(_(u"Email ") + email + _(u" already exists.")))
                            emails_exist += 1
                    # else:
                    #     messages.warning(request, str(_("Email ") + email + _(" does not exist.")))
                    #     emails_error += 1

            messages.success(request, str(_(u"Emails added.")))
            return redirect(page_client_list)
        else:
            messages.warning(request, _(u"Emails list is empty"))
            return redirect(page_client_mass_add)

    return render(request, "pages/page_client_mass_add.html", {
        'title': _("Mass add new clients"),
        'data': data,
    })


@csrf_protect
@login_required
@require_http_methods(["GET"])
def page_client_view(request, client_id):
    data = prepare_data(request)

    try:
        client = Client.objects.get(id=client_id, is_removed=False)
    except Client.DoesNotExist as error_message:
        messages.error(request, error_message)
        return redirect('home')

    content = {
        'client': client,
        'groups': Group.objects.filter(clients__in=client_id),
        'logs': Log.objects.filter(client=client),
    }

    return render(request, "pages/page_client_view.html", {
        'title': _("View client"),
        'data': data,
        'content': content,
    })


@csrf_protect
@login_required
@require_http_methods(["GET", "POST"])
def page_client_edit(request, client_id):
    data = prepare_data(request)

    try:
        client = Client.objects.get(id=client_id, is_removed=False)
    except Client.DoesNotExist as error_message:
        messages.error(request, error_message)
        return redirect('home')

    client_form = None
    if request.method == "GET":
        client_form = ClientForm(instance=client)
    elif request.method == "POST":
        if "client_edit_subscribe" in request.POST:
            if client.is_unsubscribed:
                client.is_unsubscribed = False
                client.save()
                Log.objects.create(action=9, user=request.user, client=client)
                messages.success(request, _("Subscribed"))
            else:
                messages.warning(request, _("Client already unsubscribed"))
        elif "client_edit_unsubscribe" in request.POST:
            if not client.is_unsubscribed:
                client.is_unsubscribed = True
                client.save()
                Log.objects.create(action=1, user=request.user, client=client)
                messages.success(request, _("Unsubscribed"))
            else:
                messages.warning(request, _("Client already subscribed"))
        elif "client_edit_delete" in request.POST:
            if not client.is_removed:
                client.is_removed = True
                client.save()
                Log.objects.create(action=10, user=request.user, client=client)
                messages.success(request, _("Deleted"))
                return redirect('home')
        else:
            client_form = ClientForm(request.POST, instance=client)
            if client_form.is_valid():
                # new_client = client_form.save(commit=False)
                client_form.save(commit=False)
                client_form.unsubscribe_code = md5(
                    str(request.POST['email'] + str(randint(100000, 1000000))).encode()).hexdigest()
                client_form.save()

                Log.objects.create(action=4, user=request.user, client=client)

                messages.success(request, _("Saved"))
            else:
                messages.error(request, client_form.errors)

        return redirect('client_view', client_id=client_id)

    content = {
        'client_form': client_form,
        'client': client,
    }

    return render(request, "pages/page_client_edit.html", {
        'title': _("Edit client"),
        'data': data,
        'content': content,
    })


@csrf_protect
@require_http_methods(["GET", "POST"])
def page_client_unsubscribe(request, client_id, code):
    data = prepare_data(request)

    try:
        client = Client.objects.get(id=client_id, is_removed=False, unsubscribe_code=code)
    except Client.DoesNotExist as error_message:
        messages.error(request, error_message)
        return redirect('home')

    if request.method == "GET":
        if client.is_unsubscribed:
            return redirect('client_unsubscribe_ok', client_id=client.id, code=client.unsubscribe_code)

        content = {
            'client': client,
        }

        return render(request, "pages/page_client_unsubscribe.html", {
            'title': _("Unsubscribe"),
            'data': data,
            'content': content,
        })
    elif request.method == "POST":
        client.is_unsubscribed = True
        client.save()

        messages.info(request, _("You have successfully unsubscribed."))
        Log.objects.create(action=1, client=client)

        return redirect('client_unsubscribe_ok', client_id=client.id, code=client.unsubscribe_code)


@require_http_methods(["GET"])
def page_client_unsubscribe_ok(request, client_id, code):
    data = prepare_data(request)

    try:
        client = Client.objects.get(id=client_id, is_removed=False, unsubscribe_code=code)
    except Client.DoesNotExist as error_message:
        messages.error(request, error_message)
        return redirect('home')

    if not messages.get_messages(request):
        if client.is_unsubscribed:
            messages.info(request, _("You already unsubscribed."))
        else:
            return redirect('client_unsubscribe', client_id=client.id, code=client.unsubscribe_code)

    return render(request, "pages/page_client_unsubscribe_ok.html", {
        'title': _("Unsubscribe"),
        'data': data,
    })