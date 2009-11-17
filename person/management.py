#from django.dispatch import dispatcher

#def UserProfilePostInsert(sender, instance, signal, *args, **kwargs):
	#"""
	#Inserts a blank imap server entry (if necessary) and associates it with the user
	#"""
	#user = instance
	#i = user.get_profile().imap_servers.create()
	#user.get_profile().about = 'test'
	#i.save()
    #user.save_profile()

## we want this called after every user is inserted
#dispatcher.connect(UserProfilePostInsert, signal=signals.pre_save, sender=User)
