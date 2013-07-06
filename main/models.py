from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _


class MailAccount(models.Model):
    server = models.CharField(verbose_name=_("Server"), max_length=256)
    username = models.CharField(verbose_name=_("Username"), max_length=512)
    password = models.CharField(verbose_name=_("Password"), max_length=512)
    port = models.PositiveSmallIntegerField(verbose_name=_("Port"), default=25)
    use_tls = models.BooleanField(verbose_name=_("Use TLS"), default=False)
    description = models.TextField(verbose_name=_("Description"), max_length=1024, blank=True, null=True)
    date_create = models.DateTimeField(verbose_name=_("Date of creating"), auto_now_add=True)
    counter = models.BigIntegerField(verbose_name=_("Counter"), default=0)
    # TODO add limits
    # limit_hours = models.PositiveIntegerField(default=0)
    # limit_daily = models.PositiveIntegerField(default=0)
    # limit_month = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = _('Mail accounts')
        verbose_name = _('Mail account')

    def __unicode__(self):
        return self.username


class MailingList(models.Model):
    email = models.EmailField(verbose_name=_("Email"), max_length=512)
    first_name = models.CharField(verbose_name=_("First name"), max_length=512)
    last_name = models.CharField(verbose_name=_("Last name"), max_length=512)
    description = models.TextField(verbose_name=_("Description"), max_length=1024, blank=True, null=True)
    date_create = models.DateTimeField(verbose_name=_("Date of creating"), auto_now_add=True)
    date_send_last = models.DateTimeField(verbose_name=_("Date of last send"), null=True, blank=True)

    class Meta:
        verbose_name_plural = _('Mailing lists')
        verbose_name = _('Mailing list')

    def __unicode__(self):
        return "%s %s <%s>" % (self.first_name, self.last_name, self.email)


class Project(models.Model):
    MAILING_TYPE = (
        (0, _('Copy')),
        (1, _('Private'))
    )

    name = models.CharField(verbose_name=_("Name"), max_length=64)
    description = models.TextField(verbose_name=_("Description"), max_length=1024, blank=True, null=True)
    groups = models.ManyToManyField(Group, verbose_name=_("Groups"))
    email_list = models.ManyToManyField(MailingList, verbose_name=_("Emails list"))
    date_create = models.DateTimeField(verbose_name=_("Date of creating"), auto_now_add=True)
    date_send_last = models.DateTimeField(verbose_name=_("Date of last send"), null=True, blank=True)
    from_name = models.CharField(verbose_name=_("From name"), max_length=1024)
    from_account = models.ForeignKey(MailAccount, verbose_name=_("From account"))
    mailing_type = models.PositiveSmallIntegerField(verbose_name=_("Mailing type"), choices=MAILING_TYPE, default=1)

    class Meta:
        verbose_name_plural = _('Projects')
        verbose_name = _('Project')

    def __unicode__(self):
        return "%s" % self.name


class Mailing(models.Model):
    CONTENT_TYPE = (
        ('text/plain', 'Text'),
        ('text/html', 'HTML')
    )

    subject = models.CharField(verbose_name=_("Subject"), max_length=496)
    text = models.TextField(verbose_name=_("Text"))
    content_type = models.CharField(verbose_name=_("Content type"), choices=CONTENT_TYPE, max_length=64, default=0)
    project = models.ForeignKey(Project, verbose_name=_("Project"))
    date_create = models.DateTimeField(verbose_name=_("Date of creating"), auto_now_add=True)
    # TODO Last send

    class Meta:
        verbose_name_plural = _('Mailings')
        verbose_name = _('Mailing')

    def __unicode__(self):
        return self.subject