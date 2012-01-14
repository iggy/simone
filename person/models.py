from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
from django.dispatch import dispatcher


class Signature(models.Model):
    text = models.TextField(blank=True)
    def __unicode__(self):
        return self.text[0:30]

# holds imap server connection info
# FIXME needs to be unique(address,port,username,passwd)
# FIXME also need a "friendly name" field
# FIXME also needs ssl checkbox/bool
class ImapServer(models.Model):
    address = models.CharField(max_length=255,null=True)
    port = models.CharField(max_length=5,default="143",null=True)
    username = models.CharField(max_length=255,null=True)
    passwd = models.CharField(max_length=255,null=True)
    ssl = models.BooleanField(default=False)
    def __unicode__(self):
        if not self.address and not self.port and not self.username and not self.passwd:
            return 'None'
        if self.ssl:
            return '%s@imaps://%s:%s' % (self.username, self.address, self.port)
        return '%s@imap://%s:%s' % (self.username, self.address, self.port)


class SmtpServer(models.Model):
    address = models.CharField(max_length=255,null=True)
    port = models.CharField(max_length=5,default="143",null=True)
    username = models.CharField(max_length=255,null=True)
    passwd = models.CharField("Password", max_length=255,null=True)
    def __unicode__(self):
        if not self.address and not self.port and not self.username and not self.passwd:
            return 'None'
        return '%s@smtp://%s:%s' % (self.username, self.address, self.port)

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)

    about = models.TextField(blank=True)
    editor = models.CharField(max_length=1, choices = (('1', 'Text'), ('2', 'Rich Text')), default='1')

    signatures = models.ManyToManyField(Signature,blank=True,null=True)
    imap_servers = models.ManyToManyField(ImapServer,blank=True,null=True)
    smtp_servers = models.ManyToManyField(SmtpServer,blank=True,null=True)
    
    def __unicode__(self):
        return '%s\'s UserProfile' % (self.user,)



def UserProfileExtraWork(sender, instance, signal, *args, **kwargs):
	"""
	Inserts a blank imap server entry (if necessary) and associates it with the user
	"""
	from django_webmail.person.models import UserProfile
	#user = instance
	##user.create_profile()
	##user.get_profile().about = 'test'
	##user.get_profile().save()
	#user.get_profile() = UserProfile()
	#user.get_profile().save()

	try:
		#userprofile.objects.get(user=instance)
		profile = instance.get_profile()
	except:
		new_profile = UserProfile(user=instance)
		new_profile.save()

	i = instance.get_profile().imap_servers.create()
	i.save()
	#user.save_profile()

# we want this called after every user is inserted
# FIXME - port to 1.0
#dispatcher.connect(UserProfileExtraWork, signal=signals.post_save, sender=User)
