from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


class MailAccount(models.Model):
    server = models.CharField(verbose_name=_("Server"), max_length=256)
    username = models.CharField(verbose_name=_("Username"), max_length=512)
    password = models.CharField(verbose_name=_("Password"), max_length=512)
    port = models.PositiveSmallIntegerField(verbose_name=_("Port"), default=25)
    use_tls = models.BooleanField(verbose_name=_("Use TLS"), default=False)
    description = models.TextField(verbose_name=_("Description"), max_length=1024, blank=True, null=True)
    date_creating = models.DateTimeField(verbose_name=_("Date of creating"), auto_now_add=True)
    counter = models.BigIntegerField(verbose_name=_("Counter"), default=0)
    previous_version = models.ForeignKey('MailAccount', verbose_name=_("Previous version"), null=True, blank=True,
                                         related_name='previous_version_account')
    is_removed = models.BooleanField(verbose_name=_("Removed"), default=False)
    # TODO add limits
    # limit_hours = models.PositiveIntegerField(default=0)
    # limit_daily = models.PositiveIntegerField(default=0)
    # limit_month = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = _('Mail accounts')
        verbose_name = _('Mail account')

    def __str__(self):
        return self.username


class Client(models.Model):
    email = models.EmailField(verbose_name=_("Email"), max_length=512)
    first_name = models.CharField(verbose_name=_("First name"), max_length=512)
    last_name = models.CharField(verbose_name=_("Last name"), max_length=512)
    description = models.TextField(verbose_name=_("Description"), max_length=1024, blank=True, null=True)
    unsubscribe_code = models.CharField(verbose_name=_("Unsubscribe code"), max_length=32)
    is_unsubscribed = models.BooleanField(verbose_name=_("Removed"), default=False)
    date_creating = models.DateTimeField(verbose_name=_("Date of creating"), auto_now_add=True)
    previous_version = models.ForeignKey('Client', verbose_name=_("Previous version"), null=True, blank=True,
                                         related_name='previous_version_client')
    is_removed = models.BooleanField(verbose_name=_("Removed"), default=False)

    class Meta:
        verbose_name_plural = _('Clients')
        verbose_name = _('Client')

    def __str__(self):
        return "%s %s <%s>" % (self.first_name, self.last_name, self.email)


class Project(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=64)
    description = models.TextField(verbose_name=_("Description"), max_length=1024, blank=True, null=True)
    from_name = models.CharField(verbose_name=_("From name"), max_length=1024)
    from_account = models.ForeignKey(MailAccount, verbose_name=_("From account"))
    date_creating = models.DateTimeField(verbose_name=_("Date of creating"), auto_now_add=True)
    previous_version = models.ForeignKey('Project', verbose_name=_("Previous version"), null=True, blank=True,
                                         related_name='previous_version_project')
    is_removed = models.BooleanField(verbose_name=_("Removed"), default=False)

    class Meta:
        verbose_name_plural = _('Projects')
        verbose_name = _('Project')

    def __str__(self):
        return self.name


class Group(models.Model):
    MAILING_TYPE = (
        (0, _('Copy')),
        (1, _('Private'))
    )

    name = models.CharField(verbose_name=_("Name"), max_length=64)
    project = models.ForeignKey(Project, verbose_name=_("Project"))
    description = models.TextField(verbose_name=_("Description"), max_length=1024, blank=True, null=True)
    clients = models.ManyToManyField(Client, verbose_name=_("Clients list"))
    mailing_type = models.PositiveSmallIntegerField(verbose_name=_("Mailing type"), choices=MAILING_TYPE, default=1)
    date_creating = models.DateTimeField(verbose_name=_("Date of creating"), auto_now_add=True)
    previous_version = models.ForeignKey('Group', verbose_name=_("Previous version"), null=True, blank=True,
                                         related_name='previous_version_group')
    is_removed = models.BooleanField(verbose_name=_("Removed"), default=False)

    class Meta:
        verbose_name_plural = _('Groups')
        verbose_name = _('Group')

    def __str__(self):
        return self.name


class Message(models.Model):
    CONTENT_TYPE = (
        ('plain', 'Text'),
        ('html', 'HTML')
    )

    subject = models.CharField(verbose_name=_("Subject"), max_length=496)
    text = models.TextField(verbose_name=_("Text"))
    content_type = models.CharField(verbose_name=_("Content type"), choices=CONTENT_TYPE, max_length=64, default=0)
    group = models.ForeignKey(Group, verbose_name=_("Group"))
    date_creating = models.DateTimeField(verbose_name=_("Date of creating"), auto_now_add=True)
    previous_version = models.ForeignKey('Message', verbose_name=_("Previous version"), null=True, blank=True,
                                         related_name='previous_version_message')
    is_removed = models.BooleanField(verbose_name=_("Removed"), default=False)

    class Meta:
        verbose_name_plural = _('Messages')
        verbose_name = _('Message')

    def __str__(self):
        return self.subject


class Log(models.Model):
    ACTIONS = (
        (0, _('Send mail')),
        (1, _('Unsubscribe')),
        (2, _('Edit project')),
        (3, _('Edit message')),
        (4, _('Edit client')),
    )

    date = models.DateTimeField(verbose_name=_("Date and time"), auto_now_add=True)
    action = models.PositiveSmallIntegerField(verbose_name=_("Action"), choices=ACTIONS)
    user = models.ForeignKey(User, verbose_name=_("User"), null=True, blank=True)
    from_account = models.ForeignKey(MailAccount, verbose_name=_("From account"), null=True, blank=True)
    from_project = models.ForeignKey(Project, verbose_name=_("From project"), null=True, blank=True)
    from_group = models.ForeignKey(Group, verbose_name=_("From group"), null=True, blank=True)
    message = models.ForeignKey(Message, verbose_name=_("Message"), null=True, blank=True)
    client = models.ForeignKey(Client, verbose_name=_("Client"), null=True, blank=True)
    is_removed = models.BooleanField(verbose_name=_("Removed"), default=False)

    class Meta:
        verbose_name_plural = _('Logs')
        verbose_name = _('Log')

    def __str__(self):
        return "%s: %s" % (self.date, self.get_action_display())