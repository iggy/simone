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
    #if request.user.get_profile().imap_servers.all()[0].username == None:
        #return HttpResponseRedirect('config/newconfig/')
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
def viewmsg(request, folder, uid):
    imap = imaplib.IMAP4_SSL(request.user.get_profile().imap_servers.all()[0].address)
    imap.login(request.user.get_profile().imap_servers.all()[0].username, request.user.get_profile().imap_servers.all()[0].passwd)

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
    return render_to_response('mail/viewmsg.html', locals())

@login_required
def newmail(request):
    # TODO need to figure out what email addresses they are allowed to use as from:
    # TODO also change the whole sending email to use newforms
    return render_to_response('mail/newmail.html', locals())

@login_required
def send(request):
    from django.core.mail import send_mail, BadHeaderError
    from smtplib import SMTPAuthenticationError
    # attempt to send the mail
    subject = request.POST.get('newmailsubject', '')
    message = request.POST.get('editor', '')
    mailfrom = request.POST.get('newmailfrom', '') # TODO should actually get their default from
    mailto = request.POST.get('newmailto', '') 
    if subject and message and mailfrom and mailto:
        try:
            send_mail(subject, message, mailfrom, [mailto], auth_user=request.user, auth_password=request.user.get_profile().imap_servers.all()[0].passwd)
        except BadHeaderError:
            return HttpResponse('Invalid Header Found')
        except SMTPAuthenticationError:
            return HttpResponse('Invalid SMTP server settings')
        return HttpResponse('Mail sent succesfully') # we can use short responses since we will only be submitting via ajax
    else:
        return HttpResponse('Fill in all fields'+subject+message+mailfrom+mailto) # if they get this, they've already lost their mail since we are submitting the mail via ajax

@login_required
def config(request, action):
    from person.models import UserProfile, ImapServer, SmtpServer
    if action == "newconfig":
        # we already know they don't have anything in the database, just show them a blank form
        #UserForm = forms.form_for_model(UserProfile)
        ImapForm = forms.form_for_model(ImapServer)
        #uform = UserForm()
        iform = ImapForm(initial={'address':'localhost','port':'143'})
        
    elif action == "addnew":
        # we are adding some new configuration
        ImapForm = forms.form_for_model(ImapServer)
        iform = ImapForm(request.POST)
        i = request.user.get_profile().imap_servers.create(address = request.POST.get('address'),
                        port = request.POST.get('port'),
                        username = request.POST.get('username'),
                        passwd = request.POST.get('passwd'))
        i.save()
        o = request.user.get_profile().imap_servers.remove(request.user.get_profile().imap_servers.all()[0])
        return HttpResponseRedirect('/mail/')
        
    elif action == "edit":
        
        #s = request.user.get_profile().imap_servers.get() FIXME: not finished here, but I need to go out and drink
        pass
        
    else:
        # default action / index
        imapsrvs = request.user.get_profile().imap_servers.all()
        #iforms = []
        #for srv in srvs:
            #iforms.append(forms.form_for_instance(srv))
    return render_to_response('mail/config/'+action+'.html', locals())


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
		for server in request.user.get_profile().imap_servers.all():
			srvlist.append(server.address)
		return HttpResponse(simplejson.dumps(srvlist))
	elif action == "msglist":
		msgs = []
		return HttpResponse(simplejson.dumps(msgs))
	
	