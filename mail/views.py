# Create your views here.
import email
from pprint import pprint

from django.shortcuts import render_to_response, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
from django.http import HttpResponseRedirect

def debug(*args):
	print ">>>>>>"
	for d in args:
		pprint(d)
	print "<<<<<<"

def f(p,t,c):
 s=p.split('.');a=s[0];b=s[1:]
 if b:
  if a not in c:c[a]={}
  f('.'.join(b),t,c[a])
 else:c[a]=t
#menu={}
#for i in items:f(i,i,menu)


try:
	import imapclient
except:
	print "imapclient module not available, please install it (pip install imapclient)"

try:
	import simplejson
except:
	from django.utils import simplejson

# TODO leaving index as is for a little bit more development
# index/login page
#def index(request):
#    return render_to_response('mail/index.html', locals())

@login_required
def index(request):
	# if they haven't filled in their options, we won't have much luck connecting to their mail server
	try:
		if request.user.get_profile().imap_servers.all()[0].username == None:
			pass
	except:
		return HttpResponseRedirect('config/newconfig/')

	folder = "INBOX"

	defaultEditor = request.user.get_profile().editor

	return render_to_response('mail/main.html', locals())

# FIXME handle sorting
@login_required
def msglist(request, server, folder, page, perpage, sortc, sortdir, search):
	server = int(server)
	srvr = request.user.get_profile().imap_servers.all()[server]
	pprint(srvr)

	start = int(page) * int(perpage) - int(perpage) + 1
	stop =  int(page) * int(perpage)

	server = imapclient.IMAPClient(srvr.address, use_uid=True)
	server.login(srvr.username, srvr.passwd)
	nummsgs = server.select_folder(folder)
	
	if stop > nummsgs:
		stop = nummsgs
	
	server.select_folder(folder)

	# we just need the headers for the msglist
	msglst = []
	
	fetched = server.fetch('%d:%d' % (start, stop), ['UID', 'FLAGS', 'INTERNALDATE', 'BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)]', 'RFC822.SIZE'])
	for uid in fetched:
		m = fetched[uid]
		mfrom, msubject = m['BODY[HEADER.FIELDS (FROM SUBJECT)]'].split('\r\n', 1)
		mfrom = mfrom.split(': ', 1)[1].rstrip('\r\n')
		msubject = msubject.split(': ', 1)[1].rstrip('\r\n')
		msglst.append({
			'uid': uid,
			'flags': m['FLAGS'],
			'subject': escape(msubject, u''),
			'from': escape(mfrom,  u''),
			'date': m['INTERNALDATE'].strftime('%b %d %Y - %H:%M'),
			'size': m['RFC822.SIZE'],
		})
	
	server.logout()

	return HttpResponse(simplejson.dumps({'totalmsgs':len(nummsgs), 'start': start, 'stop': stop, 'msglist': msglst}))

@login_required
def viewmsg(request, server, folder, uid):
	# these are here so they get passed through to the template
	folder = folder
	uid = int(uid)
	server = int(server)
	
	isrv = request.user.get_profile().imap_servers.all()[server]
	i = imapclient.IMAPClient(isrv.address, use_uid=True)
	i.login(isrv.username, isrv.passwd)

	i.select_folder(folder)

	mailbody = i.fetch([uid], ['BODY[]'])
	mailmsg = email.message_from_string(mailbody[uid]['BODY[]'])

	if not mailmsg.is_multipart():
		body = mailmsg.get_payload()
	else:
		for part in mailmsg.walk():
			if(part.get_content_type() == mailmsg.get_default_type()):
				body = part.get_payload().decode('quopri_codec')

	i.logout()
	
	if request.GET.get('json') == "true":
		from django.utils import simplejson
		return HttpResponse(simplejson.dumps({'headers':mailmsg.items(), 'body':body}))

	return render_to_response('mail/viewmsg.html', locals())

@login_required
def newmail(request):
	# TODO need to figure out what email addresses they are allowed to use as from:
	# TODO also change the whole sending email to use newforms
	return render_to_response('mail/newmail.html', locals())

@login_required
def send(request):
	from django.core.mail import send_mail, BadHeaderError#, EmailMultiAlternatives
	from smtplib import SMTPAuthenticationError
	#from django.utils import simplejson

	# attempt to send the mail
	subject = request.POST.get('newmailsubject', '')
	message = request.POST.get('editor', '')
	mailfrom = request.POST.get('newmailfrom', '') # TODO should actually get their default from
	mailto = request.POST.get('newmailto', '')

	if request.POST.get('usingRTE') == "true":
		message = '<html><head></head>' + message + '</html>'

	if subject and message and mailfrom and mailto:
		try:
			send_mail(subject, message, mailfrom, [mailto], auth_user=request.user, auth_password=request.user.get_profile().smtp_servers.all()[0].passwd)
			# FIXME send plain text part as well as html part
			#msg = EmailMultiAlternatives(subject, message, mailfrom, [mailto])
			#if request.POST.get('usingRTE') == "true":
				#msg.content_subtype = "html"
			#msg.send(auth_user=request.user, auth_password=request.user.get_profile().smtp_servers.all()[0].passwd)
		except BadHeaderError:
			return HttpResponse(simplejson.dumps({'status':'ERROR', 'message': 'Invalid Header Found'}))
		except SMTPAuthenticationError:
			return HttpResponse(simplejson.dumps({'status':'ERROR', 'message': 'Invalid SMTP server settings'}))
		return HttpResponse(simplejson.dumps({'status':'SUCCESS', 'message': 'Mail sent succesfully'})) # we can use short responses since we will only be submitting via ajax
	else:
		return HttpResponse(simplejson.dumps({'status':'ERROR', 'message': 'Fill in all fields'+subject+message+mailfrom+mailto}))

@login_required
def config(request, action):
    from mail.forms import ImapServerForm, SmtpServerForm

    if action == "newconfig" or action == "newIMAPform":
        # we already know they don't have anything in the database, just show them a blank form
        iform = ImapServerForm(initial={'address':'localhost','port':'143'})
        srvtype = "IMAP"

    elif action == "newSMTPform":
        sform = SmtpServerForm(initial={'address':'localhost','port':'25'})
        srvtype = "SMTP"

    elif action == "addnew":
        if request.POST.get('newconfig') == "true":
            for srv in request.user.get_profile().imap_servers.all():
                request.user.get_profile().imap_servers.remove(srv)

        # we are adding some new configuration
        iform = ImapServerForm(request.POST)
        i = request.user.get_profile().imap_servers.create(address = request.POST.get('address'),
                        port = request.POST.get('port'),
                        username = request.POST.get('username'),
                        passwd = request.POST.get('passwd'))
        i.save()

        # if they didn't have a "real" imap server setup before delete the fake one
        #if request.user.get_profile().imap_servers.all()[0].username == None:
            #o = request.user.get_profile().imap_servers.remove(0)
            #o = request.user.get_profile().imap_servers.remove(request.user.get_profile().imap_servers.all()[0])
        return HttpResponseRedirect('/mail/')

    elif action == "addnewsmtp":
        sform = SmtpServerForm(request.POST)
        s = request.user.get_profile().smtp_servers.create(address = request.POST.get('address'),
                        port = request.POST.get('port'),
                        username = request.POST.get('username'),
                        passwd = request.POST.get('passwd'))
        s.save()
        return HttpResponse(simplejson.dumps({'status':'OK'}))

    elif action == "edit":
        saction = request.GET.get('saction')
        srvtype = request.GET.get('srvtype')
        whichsrv = int(request.GET.get('which'))

        if saction == "REMOVE":
            srv = request.user.get_profile().imap_servers.remove(request.user.get_profile().imap_servers.all()[whichsrv])

        return HttpResponse(simplejson.dumps({'status':'OK'}))
    else:
        # default action / index
        imapsrvs = request.user.get_profile().imap_servers.all()
        # the code below uses newforms, but these forms are so short it turned out working better to just hand code them

    return render_to_response('mail/config/'+action+'.html', locals())

#def form_callback(f, **args):
    #if f.name == "passwd":
        #return forms.PasswordInput()
    #return f.formfield(**args)
#def form_callback(f, **args):
    #formfield = f.formfield(**args)
    #if f.name == "passwd":
        #formfield.widget = forms.PasswordInput()
    #return formfield

@login_required
def json(request, action):
	uprof = request.user.get_profile()

	if action == "folderlist":
		server = int(request.GET['server'])
		srvr = uprof.imap_servers.all()[server]

		imap = imapclient.IMAPClient(srvr.address, use_uid=True)
		imap.login(srvr.username, srvr.passwd)
		flist = imap.list_folders()
		imap.logout()
		
		delimiter = flist[0][1]
		
		# FIXME use list of subscribed folders
		return HttpResponse(simplejson.dumps({
			'delimiter': flist[0][1],
			'folders': [z for x,y,z in flist]
		}))
		
	if action == "folderlist2":
		server = int(request.GET['server'])
		srvr = uprof.imap_servers.all()[server]

		imap = imapclient.IMAPClient(srvr.address, use_uid=True)
		imap.login(srvr.username, srvr.passwd)
		flist = imap.list_folders()
		imap.logout()
		
		debug(flist)
		
		done = []
		jstreefolders = []
		
		#def old_f(p,t,c):
			#if '.' not in p:
				#c[p]=t
				#return
			#a,b=p.split('.', 1)
			#if b:
				#if a not in c:c[a]={}
				#f('.'.join(b),t,c[a])
			#else:c[a]=t
			
		#def rec(path, fullpath, fdict, sep):
			#segs = path.split(sep)
			#a = segs[0]
			#b = segs[1:]
			#if not b:
				#try:
					#fdict[a] = fullpath
				#except:
					#fdict = {}
					#fdict[a] = fullpath
			#else:
				##debug("fdict[a] = ", fdict[a], fdict, a)
				##if fdict[a] == a:
					##fdict[a] = {}
				#if a not in fdict:
					#fdict[a] = {}
				#debug(jstreefolders)
				#rec(sep.join(b), fullpath, fdict[a], sep)
				
		sortedlist = sorted(flist)
		debug(sortedlist)
		for flags, delim, fld in flist:
			debug(flags, delim, fld)
			#f(fld,fld,jstreefolders)
			#rec(fld, fld, jstreefolders, delim)
			
			
			if fld.split(delim)[0] in done:
				continue
			done.append(fld.split(delim)[0])
			
			#if delim not in fld:
			if '\\HasNoChildren' in flags:
				jstreefolders.append({
					'title': fld.split(delim)[0],
					'data': fld.split(delim)[0],
					#'metadata': {'id':fld},
					'attr': {'rel':'folder'},
				})
			else:
				jstreefolders.append({
					'title': fld.split(delim)[0],
					'data': fld.split(delim)[0],
					'state': 'closed',
					'attr': {'rel':'folder'},
					#'metadata': {'id': fld},
				})
		
		
		jstreefolders.append({
			'title': 'Test1',
			'state': 'closed',
			'attr': {'rel':'folder'},
			'children': [
				'Test2', 
				'Test3',
				{'title': 'Test4','state':'closed','attr': {'rel':'folder'},},
				{'title': 'Test5','state':'closed','attr': {'rel':'folder'},'children':[]}
			]
		})
		
		resp = {'data': jstreefolders}
		
		debug(resp)
		
		# FIXME use list of subscribed folders
		return HttpResponse(simplejson.dumps(jstreefolders))

	elif action == "serverlist":
		srvlist = []
		i = 0
		for i, server in enumerate(uprof.imap_servers.all()):
			srvlist.append([i, server.address])
		return HttpResponse(simplejson.dumps({'servers':srvlist}))

@login_required
def action(request, action):
	# a few vars that get used in (almost) every action
	server = int(request.GET.get('server'))
	folder = request.GET.get('folder')

	# get the server
	try:
		my_imap_server = request.user.get_profile().imap_servers.all()[server]
	except (IndexError, TypeError):
		return HttpResponse(simplejson.dumps({'error':'Invalid server'}))

	server = imapclient.IMAPClient(my_imap_server.address, use_uid=True)
	server.login(my_imap_server.username, my_imap_server.passwd)
	nummsgs = server.select_folder(folder)

	rstat = "SUCCESS"
	if action == 'markread':
		try:
			uid = request.GET.get('uid')
			rtext = server.add_flags([uid], [imapclient.SEEN])
		except:
			rstat = 'FAILURE'
	elif action == 'markunread':
		try:
			uid = request.GET.get('uid')
			rtext = server.remove_flags([uid], [imapclient.SEEN])
		except:
			rstat = 'FAILURE'
	elif action == 'markimportant':
		try:
			uid = request.GET.get('uid')
			rtext = server.add_flags([uid], [imapclient.FLAGGED])
		except:
			rstat = 'FAILURE'


	return HttpResponse(simplejson.dumps({'status':rstat, 'msg':rtext}))

def escape(s, quote=None):
	'''replace special characters "&", "<" and ">" to HTML-safe sequences.
	If the optional flag quote is true, the quotation mark character (")
	is also translated.

	copied from python's cgi module and slightly
	massaged.'''
	if s is None:
		return ""
	s = s.replace("&", "&amp;") # Must be done first!
	s = s.replace("<", "&lt;")
	s = s.replace(">", "&gt;")
	if quote:
		s = s.replace('"', "&quot;")
	return s
