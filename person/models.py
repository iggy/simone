from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals
from django.dispatch import dispatcher


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
    editor = models.CharField(maxlength=1, choices = (('1', 'Text'), ('2', 'Rich Text')), default='1')

    signatures = models.ManyToManyField(Signature)
    imap_servers = models.ManyToManyField(ImapServer)
    smtp_servers = models.ManyToManyField(SmtpServer)



def UserProfileExtraWork(sender, instance, signal, *args, **kwargs):
	"""
	Inserts a blank imap server entry (if necessary) and associates it with the user
	"""
	from person.models import UserProfile
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
dispatcher.connect(UserProfileExtraWork, signal=signals.post_save, sender=User)
