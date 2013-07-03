from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import ugettext as _


class MailAccount(models.Model):
    smtp_server = models.CharField(max_length=256)
    smtp_user = models.CharField(max_length=512)
    smtp_password = models.CharField(max_length=512)
    description = models.TextField(max_length=1024)
    date_create = models.DateTimeField(auto_now_add=True)
    counter = models.BigIntegerField(default=0)
    # TODO add limits
    # limit_hours = models.PositiveIntegerField(default=0)
    # limit_daily = models.PositiveIntegerField(default=0)
    # limit_month = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = _('Mail accounts')
        verbose_name = _('Mail account')

    def __unicode__(self):
        return "%s on %s" % (self.smtp_user, self.smtp_server)


class MailingList(models.Model):
    email = models.EmailField(max_length=512)
    first_name = models.CharField(max_length=512)
    last_name = models.CharField(max_length=512)
    description = models.TextField(max_length=1024)
    date_create = models.DateTimeField(auto_now_add=True)
    date_send_last = models.DateTimeField(null=True)

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

    name = models.CharField(max_length=64)
    description = models.TextField(max_length=1024)
    group = models.ForeignKey(Group)
    email_list = models.ManyToManyField(MailingList)
    date_create = models.DateTimeField(auto_now_add=True)
    date_send_last = models.DateTimeField(null=True)
    from_name = models.CharField(max_length=1024)
    from_account = models.ForeignKey(MailAccount)
    mailing_type = models.PositiveSmallIntegerField(choices=MAILING_TYPE, default=1)

    class Meta:
        verbose_name_plural = _('Projects')
        verbose_name = _('Project')

    def __unicode__(self):
        return "%s for %s" % (self.name, self.group)


class Mailing(models.Model):
    CONTENT_TYPE = (
        ('text/plain', 'Text'),
        ('text/html', 'HTML')
    )

    subject = models.CharField(max_length=496)
    text = models.TextField()
    content_type = models.CharField(choices=CONTENT_TYPE, max_length=64)
    project = models.ForeignKey(Project)
    date_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = _('Mailings')
        verbose_name = _('Mailing')

    def __unicode__(self):
        return self.subject