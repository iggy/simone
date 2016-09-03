# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db import models
# from django.contrib.auth.models import AbstractUser


# @python_2_unicode_compatible
# class Signature(models.Model):
#     text = models.TextField(blank=True)
#     def __str__(self):
#         return self.text[0:30]


# holds imap server connection info
# FIXME needs to be unique(address,port,username,passwd)
# FIXME also need a "friendly name" field
# FIXME also needs ssl checkbox/bool
@python_2_unicode_compatible
class ImapServer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=255,null=True)
    port = models.IntegerField(default=143,null=True)
    username = models.CharField(max_length=255,null=True)
    passwd = models.CharField(max_length=255,null=True)
    ssl = models.BooleanField(default=False)
    def __str__(self):
        if not self.address and not self.port and not self.username and not self.passwd:
            return 'None'
        if self.ssl:
            return '%s@imaps://%s:%s' % (self.username, self.address, self.port)
        return '%s@imap://%s:%s' % (self.username, self.address, self.port)


@python_2_unicode_compatible
class SmtpServer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=255,null=True)
    port = models.IntegerField(default=25,null=True)
    username = models.CharField(max_length=255,null=True)
    passwd = models.CharField("Password", max_length=255,null=True)
    def __str__(self):
        if not self.address and not self.port and not self.username and not self.passwd:
            return 'None'
        return '%s@smtp://%s:%s' % (self.username, self.address, self.port)

# @python_2_unicode_compatible
# class UserProfile(AbstractUser):
#     about = models.TextField(blank=True)
#     editor = models.CharField(max_length=1,
#         choices = (('1', 'Text'), ('2', 'Rich Text')),
#         default='1')
#
#     signatures = models.ManyToManyField(Signature,blank=True,null=True)
#     imap_servers = models.ManyToManyField(ImapServer,blank=True,null=True)
#     smtp_servers = models.ManyToManyField(SmtpServer,blank=True,null=True)
#
#     def __str__(self):
#         return '%s\'s UserProfile' % (self.username,)
