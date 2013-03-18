#from django.forms import ModelForm, fields
from django import forms
from person.models import UserProfile, ImapServer, SmtpServer

class ImapServerForm(forms.ModelForm):
    class Meta:
        model = ImapServer
        widgets = {
            'passwd': forms.PasswordInput(),
        }
        
class SmtpServerForm(forms.ModelForm):
    class Meta:
        model = SmtpServer