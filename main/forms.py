from django.forms import ModelForm, TextInput, Textarea
from main.models import Client

__author__ = 'delin'


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ('first_name', 'last_name', 'email', 'description')
        widgets = {
            'email': TextInput(attrs={'class': 'input-xxlarge'}),
            'first_name': TextInput(attrs={'class': 'input-xxlarge'}),
            'last_name': TextInput(attrs={'class': 'input-xxlarge'}),
            'description': Textarea(attrs={'cols': 80, 'rows': 4, 'class': 'input-xxlarge'}),
        }