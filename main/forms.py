from django.forms import ModelForm, TextInput, Textarea
from main.models import Client, Project, Group

__author__ = 'delin'


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ('first_name', 'last_name', 'email', 'description', 'is_unsubscribed')
        widgets = {
            'email': TextInput(attrs={'class': 'input-xxlarge'}),
            'first_name': TextInput(attrs={'class': 'input-xxlarge'}),
            'last_name': TextInput(attrs={'class': 'input-xxlarge'}),
            'description': Textarea(attrs={'cols': 80, 'rows': 4, 'class': 'input-xxlarge'}),
        }


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'from_name', 'from_account')
        widgets = {
            'name': TextInput(attrs={'class': 'input-xxlarge'}),
            'description': Textarea(attrs={'cols': 80, 'rows': 4, 'class': 'input-xxlarge'}),
            'from_name': TextInput(attrs={'class': 'input-xxlarge'}),
        }


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'project', 'description', 'clients', 'mailing_type')
        widgets = {
            'name': TextInput(attrs={'class': 'input-xxlarge'}),
            'description': Textarea(attrs={'cols': 80, 'rows': 4, 'class': 'input-xxlarge'}),
        }