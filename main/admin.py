from django.contrib import admin
from main.models import MailAccount, Client, Project, Message, Group

__author__ = 'delin'


admin.site.register(MailAccount)
admin.site.register(Client)
admin.site.register(Project)
admin.site.register(Message)
admin.site.register(Group)