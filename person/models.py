from django.db import models
from django.contrib.auth.models import User


class Signature(models.Model):
    text = models.TextField(blank=True)
    def __str__(self):
        return self.text[0:30]

# holds imap server connection info
# FIXME needs to be unique(address,port,username,passwd)
# FIXME also need a "friendly name" field
# FIXME also needs ssl checkbox/bool
class ImapServer(models.Model):
    address = models.CharField(maxlength=255,null=True)
    port = models.CharField(maxlength=5,default="143",null=True)
    username = models.CharField(maxlength=255,null=True)
    passwd = models.CharField(maxlength=255,null=True)
    def __str__(self):
        if not self.address and not self.port and not self.username and not self.passwd:
            return 'None'
        return '%s@imap://%s:%s' % (self.username, self.address, self.port)

class SmtpServer(models.Model):
    address = models.CharField(maxlength=255,null=True)
    port = models.CharField(maxlength=5,default="143",null=True)
    username = models.CharField(maxlength=255,null=True)
    passwd = models.CharField("Password", maxlength=255,null=True)
    def __str__(self):
        if not self.address and not self.port and not self.username and not self.passwd:
            return 'None'
        return '%s@smtp://%s:%s' % (self.username, self.address, self.port)

class UserProfile( models.Model ):
    user = models.ForeignKey (User, unique=True, edit_inline=models.TABULAR,
            num_in_admin=1, min_num_in_admin=1, max_num_in_admin=1,
            num_extra_on_change=0)

    about = models.TextField(blank=True, core=True)

    signatures = models.ManyToManyField(Signature)
    imap_servers = models.ManyToManyField(ImapServer)
    smtp_servers = models.ManyToManyField(SmtpServer)
