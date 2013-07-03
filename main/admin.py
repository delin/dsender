from django.contrib import admin
from main.models import MailAccount, MailingList, Project, Mailing

__author__ = 'delin'


admin.site.register(MailAccount)
admin.site.register(MailingList)
admin.site.register(Project)
admin.site.register(Mailing)
