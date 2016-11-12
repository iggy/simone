from django import forms
from .models import ImapServer, SmtpServer

class ImapServerForm(forms.ModelForm):
    class Meta:
        model = ImapServer
        exclude = ['user']
        widgets = {
            'passwd': forms.PasswordInput(),
        }

class SmtpServerForm(forms.ModelForm):
    class Meta:
        model = SmtpServer
        exclude = ['user']
        widgets = {
            'passwd': forms.PasswordInput(),
        }
