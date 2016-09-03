from django.contrib import admin

from .models import ImapServer, SmtpServer  #, Signature

admin.site.register(ImapServer)
admin.site.register(SmtpServer)
# admin.site.register(Signature)
