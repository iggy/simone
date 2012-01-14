from django.contrib import admin

from django_webmail.person.models import UserProfile, ImapServer, SmtpServer, Signature

admin.site.register(UserProfile)
admin.site.register(ImapServer)
admin.site.register(SmtpServer)
admin.site.register(Signature)