# Create your views here.
import imaplib, re, email
from pprint import pprint

from django.shortcuts import render_to_response, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
from django.http import HttpResponseRedirect

from mail import imaplib2
from mail.dateutil import parser

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
	if request.user.get_profile().imap_servers.all()[0].username == None:
		return HttpResponseRedirect('config/newconfig/')

	folder = "INBOX"

	defaultEditor = request.user.get_profile().editor

	return render_to_response('mail/main.html', locals())

@login_required
def msglist(request, server, folder, page, perpage, sortc, sortdir, search):
	server = int(server)
	srvr = request.user.get_profile().imap_servers.all()[server]
	pprint(srvr)

	start = int(page) * int(perpage) - int(perpage) + 1
	stop =  int(page) * int(perpage)

	imap = imaplib2.IMAP4(srvr.address, srvr.username, srvr.passwd)

	if stop > len(imap[folder]):
		stop = len(imap[folder])

	# we just need the headers for the msglist
	msglst = []
	for m in imap[folder][start:stop]:
		e = m['email']
		msglst.append({
			'uid': m['uid'],
			'flags': m['flags'],
			'subject': escape(e.get('subject',  str(''))),
			'from': escape(e.get('from'),  u''),
			'date': parser.parse(m['date']).strftime('%b %d %Y - %H:%M'),
			'size': m['size'],
		})

	return HttpResponse(simplejson.dumps({'totalmsgs':len(imap[folder]), 'start': start, 'stop': stop, 'msglist': msglst}))

@login_required
def viewmsg(request, server, folder, uid):
	# TODO convert to imapclient.py
	# these are here so they get passed through to the template
	folder = folder
	uid = uid
	server = int(server)
	isrv = request.user.get_profile().imap_servers.all()[server]
	imap = imaplib.IMAP4_SSL(isrv.address)
	imap.login(isrv.username, isrv.passwd)

	countup = imap.select(folder, True)

	mailbody = imap.uid("FETCH", uid, "(BODY[])")
	mailmsg = email.message_from_string(mailbody[1][0][1])
	mail = re.search(r'(.*)^$(.*)', mailbody[1][0][1], re.M)

	header = mail.group(1)

	if not mailmsg.is_multipart():
		body = mailmsg.get_payload()
	else:
		for part in mailmsg.walk():
			if(part.get_content_type() == mailmsg.get_default_type()):
				body = part.get_payload().decode('quopri_codec')
	imap.logout()

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
    #from django.utils import simplejson
    from person.models import UserProfile, ImapServer, SmtpServer

    if action == "newconfig" or action == "newIMAPform":
        # we already know they don't have anything in the database, just show them a blank form
        #UserForm = forms.form_for_model(UserProfile)
        ImapForm = forms.form_for_model(ImapServer)
        #uform = UserForm()
        iform = ImapForm(initial={'address':'localhost','port':'143'})
        srvtype = "IMAP"

    elif action == "newSMTPform":
        SmtpForm = forms.form_for_model(SmtpServer)
        sform = SmtpForm(initial={'address':'localhost','port':'25'})
        srvtype = "SMTP"

    elif action == "addnew":
        if request.POST.get('newconfig') == "true":
            for srv in request.user.get_profile().imap_servers.all():
                request.user.get_profile().imap_servers.remove(srv)

        # we are adding some new configuration
        ImapForm = forms.form_for_model(ImapServer)
        iform = ImapForm(request.POST)
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
        SmtpForm = forms.form_for_model(SmtpServer)
        sform = SmtpForm(request.POST)
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

        #s = request.user.get_profile().imap_servers.get() FIXME: not finished here, but I need to go out and drink
        return HttpResponse(simplejson.dumps({'status':'OK'}))
    else:
        # default action / index
        imapsrvs = request.user.get_profile().imap_servers.all()
        # the code below uses newforms, but these forms are so short it turned out working better to just hand code them
        #iforms = []
        #for i in imapsrvs:
            #IForm = forms.form_for_instance(i, formfield_callback=form_callback)
            ##IForm.base_fields['passwd'].widget = forms.PasswordInput()
            #f = IForm()
            #iforms.append(f)


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
		imap = imaplib2.IMAP4(srvr.address, srvr.username, srvr.passwd)
		# FIXME delimiter shouldn't be fixed
		return HttpResponse(simplejson.dumps({'delimiter':'.', 'folders':imap.list_folders()}))

	elif action == "serverlist":
		srvlist = []
		i = 0
		for i, server in enumerate(uprof.imap_servers.all()):
			srvlist.append([i, server.address])
		return HttpResponse(simplejson.dumps({'servers':srvlist}))

@login_required
def action(request, action):
	#from django.utils import simplejson
	import imapclient as imapclient

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
			rstat = 'SUCCESS'
		except:
			rstat = 'FAILURE'
	elif action == 'markunread':
		try:
			uid = request.GET.get('uid')
			rtext = server.remove_flags([uid], [imapclient.SEEN])
			rstat = 'SUCCESS'
		except:
			rstat = 'FAILURE'
	elif action == 'markimportant':
		try:
			uid = request.GET.get('uid')
			rtext = server.add_flags([uid], [imapclient.FLAGGED])
			rstat = 'SUCCESS'
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
