# Create your views here.
import imaplib, re, email
from django.shortcuts import render_to_response, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import newforms as forms
from django.http import HttpResponseRedirect

# list messages in an imap folder
# if start isn't set
def imaplist(imap, folder="INBOX", number=20, start=None):
    # get the list of messages in INBOX
    countup = imap.select(folder, True)
    count = int(countup[1][0])
    if(start==None):
        # default usage, fetch the last number messages from the folder
        start = count-number
        if(start < 0):
            start = 1
        messageset = repr(start)+":*"
    else:
        if(count < number):
            # if there's not at least "number" messages in the folder just list them all
            count = "*"
            start = "1"
        messageset = repr(start+":"+count)
    #return messageset
    status, data = imap.fetch(messageset, "(UID RFC822.SIZE FLAGS BODY[HEADER.FIELDS (SUBJECT DATE FROM)])")
    msglist = []
    for msg in data:
        #msglist.append(repr(msg))
        if(isinstance(msg, tuple)):
            stat, hdr = msg
            #r = re.compile('subject:', re.IGNORECASE)
            msgtext = repr(msg)
            m = email.message_from_string(msgtext)

            # round up all the info we need
            subj = re.search(r'subject:(.*?)\\r\\n', msgtext, re.I)
            fromm = re.search(r'from:(.*?)\\r\\n', msgtext, re.I)
            datee = re.search(r'date:(.*?)\\r\\n', msgtext, re.I)
            uid = re.search(r'UID (.*?) ', msgtext, re.I)
            size = re.search(r'RFC822.SIZE (.*?) ', msgtext, re.I)
            flags = re.search(r'FLAGS \((.*?)\) ', msgtext, re.I)

            subjtext = subj.group(1).strip().strip('"')
            # sometimes names are name + email, sometimes just email
            try:
                fromemail = fromm.group(1).split('<')[1].strip().strip('"').strip('>')
                fromtext = fromm.group(1).split('<')[0].strip().strip('"').replace('\\', '')
            except:
                fromemail = fromm.group(1).strip().strip('"').replace('\\', '')
                fromtext = fromm.group(1).strip().strip('"').replace('\\', '')+' '
            try:
                datetext = datee.group(1).strip().strip('"')
            except:
                datetext = "blank"
            uidtext = uid.group(1).strip().strip('"')
            sizetext = size.group(1).strip().strip('"')
            flagstext = flags.group(1).strip().strip('"')

            #msglist.append([m['subject'],m['from'],m['from'],m['date'],uidtext,sizetext,flagstext,m])
            msglist.append([
                subjtext,
                fromemail,
                fromtext,
                datetext,
                uidtext,
                sizetext,
                flagstext
            ])
            #msglist.append(msg) # it's our second match
    return msglist

# TODO leaving index as is for a little bit more development
# index/login page
#def index(request):
#    return render_to_response('mail/index.html', locals())

@login_required
def index(request):
    # if they haven't filled in their options, we won't have much luck connecting to their mail server
    if request.user.get_profile().imap_servers.all()[0].username == None:
        return HttpResponseRedirect('config/newconfig/')
    # FIXME need to get the above working

    import time
    imap_conn_st = time.time()
    imap = imaplib.IMAP4_SSL(request.user.get_profile().imap_servers.all()[0].address)
    con_time = time.time() - imap_conn_st
    imap.login(request.user.get_profile().imap_servers.all()[0].username, request.user.get_profile().imap_servers.all()[0].passwd)
    log_time = time.time() - imap_conn_st
    status, list = imap.list()  # returns status of the command and the results of the command as a list
                                # the values are oddly formatted, so we have to do a little bit of parsing
    list_time = time.time() - imap_conn_st
    # get the list of folders
    # we want to break up all the subdirs into nested dicts
    #fldlist = {}
    fldlist = []
    for fld in list:
        folder = fld.split('" "')
        nm = folder[1].strip('"')  # full folder name
        # TODO the folder "parsing" shouldn't be in the template, it should be here
        #nmcopy = nm
        #splitnm = nmcopy.split('.')
        #snm = splitnm[-1]
        #nm = fld
        fldlist.append(nm)
        #if(nm.count(".")):
            #fldlist.fromkeys(nm.split('.'))
        #else:
            #fldlist.fromkeys(nm)
            ## folders in imap are seperated by .'s
            #for sub in nm.split('.'):
                #try:
                    #thisfldlist.append(sub)
                #except:
                    #thisfldlist = fldlist[sub]
                    #thisfldlist.append(sub)
            ## folders in imap are seperated by .'s
            #for sub in nm.split('.'):

                ##if not fldlist[sub]:
                #fldlist[sub] = {}
                #fldlist[sub][sub] = ''
            ## FIXME handle recursion
            #pass
        #else:
            ## if it's a top level folder, just drop it in there empty
            #fldlist[nm] = ''
    maildir = fldlist

    folder = "INBOX"

    msglist = imaplist(imap, folder)

    #countup = imap.select()
    #imap.store("1", '-FLAGS', '\\Seen')

    defaultEditor = request.user.get_profile().editor

    # clean up
    imap.logout()

    return render_to_response('mail/main.html', locals())

@login_required
def msglist(request, folder_name):
    imap = imaplib.IMAP4_SSL(request.user.get_profile().imap_servers.all()[0].address)
    imap.login(request.user.get_profile().imap_servers.all()[0].username, request.user.get_profile().imap_servers.all()[0].passwd)

    msglist = imaplist(imap, folder_name)

    # also pass folder_name to the template
    folder = folder_name

    # clean up
    imap.logout()
    return render_to_response('mail/msglist.html', locals())

@login_required
def viewmsg(request, server, folder, uid):
	# TODO convert to imapclient.py
	server = int(server)
	imap = imaplib.IMAP4_SSL(request.user.get_profile().imap_servers.all()[server].address)
	imap.login(request.user.get_profile().imap_servers.all()[server].username, request.user.get_profile().imap_servers.all()[server].passwd)

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

	#my_imap_server = request.user.get_profile().imap_servers.all()[server]

	#server = IMAPClient(my_imap_server.address, use_uid=True)
	#server.login(my_imap_server.username, my_imap_server.passwd)
	#nummsgs = server.select_folder(folder)

	#server.fetch

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
    import simplejson

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
    import simplejson
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
	import simplejson
	from imapclient import IMAPClient

	if action == "folderlist":
		try:
			which = int(request.GET.get('server'))
			my_imap_server = request.user.get_profile().imap_servers.all()[which]
		except (IndexError, TypeError):
			return HttpResponse(simplejson.dumps({'error':'Invalid server'}))
		server = IMAPClient(my_imap_server.address, use_uid=True)
		server.login(my_imap_server.username, my_imap_server.passwd)
		dirs = server.list_folders()
		return HttpResponse(simplejson.dumps(dirs))

	elif action == "serverlist":
		srvlist = []
		i = 0
		for i, server in enumerate(request.user.get_profile().imap_servers.all()):
			srvlist.append([i, server.address])
		return HttpResponse(simplejson.dumps({'servers':srvlist}))

	elif action == "msglist":
		import dateutil.parser as parser

		try:
			start = request.GET['start']
			end = request.GET['end']
		except:
			start = repr(1)
			end = repr(20)
		msgs = []

		# get the server
		try:
			which = int(request.GET.get('server'))
			my_imap_server = request.user.get_profile().imap_servers.all()[which]
		except (IndexError, TypeError):
			return HttpResponse(simplejson.dumps({'error':'Invalid server'}))

		# get the folder
		folder = request.GET.get('folder')

		server = IMAPClient(my_imap_server.address, use_uid=True)
		server.login(my_imap_server.username, my_imap_server.passwd)
		nummsgs = server.select_folder(folder)

		if int(end) > nummsgs:
			end = repr(nummsgs)

		#server.use_uid = False
		#alluids = server.search('ALL')
		fmsgs = server.fetch(start+":"+end, ["UID", "RFC822.SIZE", "FLAGS"])
		fmsgs2 = server.fetch(start+":"+end, ["BODY[HEADER.FIELDS (SUBJECT DATE FROM)]"])
		#msgs = server._imap.imaplist(folder)
		#msgs = server.search()

		for msg in fmsgs:
			# need to parse out the parts, can't just send them straight to the browser
			#uid = fmsgs[msg]['UID']
			size = fmsgs[msg]['RFC822.SIZE']
			header = fmsgs2[msg]['BODY[HEADER.FIELDS (SUBJECT DATE FROM)]']
			#subject = re.search('subject:', header, re.I)
			subject = re.search(r'subject:(.*?)\r\n', header, re.I).group(1).strip().strip('"')
			mfrom = re.search(r'from:(.*?)\r\n', header, re.I)
			try:
				fromemail = mfrom.group(1).split('<')[1].strip().strip('"').strip('>')
				fromtext = mfrom.group(1).split('<')[0].strip().strip('"').replace('\\', '')
			except:
				fromemail = mfrom.group(1).strip().strip('"').replace('\\', '')
				fromtext = mfrom.group(1).strip().strip('"').replace('\\', '')+' '
			fromemail = re.search(r'from: (<([^\]]+)|(.*))\r\n', header, re.I).group(1)
			mdate = re.search(r'date:(.*?)\r\n', header, re.I)
			#dateutilo = dateutil
			dateo = parser.parse(mdate.group(1), ignoretz=True)
			datetext = dateo.isoformat()
			flags = fmsgs[msg]['FLAGS']

			# reset the msgs flags to what they were before we fetch'ed the headers
			server.set_flags(msg, flags)

			msgs.append({'uid':msg, 'size': size, 'subject': subject, 'fromtext':fromtext, 'fromemail':fromemail, 'date':datetext, 'flags':flags, 'folder':folder, 'server':which})

		return HttpResponse(simplejson.dumps({'name': folder, 'count': nummsgs, 'start':start, 'end':end, 'msgs': msgs, 'records':int(end)-int(start)}))



@login_required
def action(request, action):
	import simplejson
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

	if action == 'markread':
		pass
	elif action == 'markunread':
		try:
			uid = request.GET.get('uid')
			server.remove_flags([uid], [imapclient.SEEN])
			returnstatus = 'SUCCESS'
		except:
			returnstatus = 'FAILURE'


	return HttpResponse(simplejson.dumps({'status':returnstatus}))