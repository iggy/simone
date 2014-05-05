# Create your views here.
import email
import json
import smtplib
import sys
from pprint import pprint

from django.shortcuts import render, render_to_response, HttpResponse
#, JsonResponse Django 1.7
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import RequestContext

def debug(*args):
    #return
    print ">>>>>>"
    for arg in args:
        pprint(arg)
    print "<<<<<<"

try:
    import imapclient
except:
    print "imapclient module not available, please install it (pip install imapclient)"

@login_required
def index(request):
    """main index view

    :param request: request object from Django
    """
    # if they haven't filled in their options, we won't have much luck 
    # connecting to their mail server
    try:
        if request.user.imap_servers.all()[0].username == None:
            pass
    except:
        return HttpResponseRedirect('config/newconfig/')

    folder = "INBOX"

    defaultEditor = request.user.editor

    return render_to_response('mail/main.html', locals())

# FIXME handle sorting
@login_required
def msglist(request, server, folder, page, perpage, sortc, sortdir, search):
    """return the list of messages as json data
    
    :param request: request object from Django
    :param server: server number
    :param folder: folder to grab messages
    :param page: which page (set of messages) to fetch
    :param perpage: how many messages to show per page
    :param sortc: which column to sort on
    :param sortdir: direction to sort (asc, desc)
    :param search: search terms (urlencoded)
    """
    server = int(server)
    srvr = request.user.imap_servers.all()[server]

    imap = imapclient.IMAPClient(srvr.address, port=srvr.port, use_uid=False, ssl=srvr.ssl)
    imap.login(srvr.username, srvr.passwd)
    folder_info = imap.select_folder(folder)
    
    if search == "":
        search = u'ALL'
    try:
        tofetch = imap.sort("ARRIVAL", search)
    except:
        exctype, value = sys.exc_info()[:2]
        return HttpResponse(json.dumps({'status': 'ERROR', 'message': str(value)}))
    
    nummsgs = len(tofetch)
    
    start = int(page) * int(perpage) - int(perpage) + 1
    stop = int(page) * int(perpage)

    if stop > nummsgs:
        stop = nummsgs
    
    if sortdir == u'D':
        start = nummsgs - int(page) * int(perpage)
        stop = nummsgs - int(int(page) - 1) * int(perpage)
    
    # we just need the headers for the msglist
    msglst = {}
    
    fetched = imap.fetch(tofetch[start:stop], ['UID', 'FLAGS', 'INTERNALDATE', 'BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)]', 'RFC822.SIZE'])
    
    for uid in fetched:
        try:
            m = fetched[uid]
            msg = email.message_from_string(m['BODY[HEADER.FIELDS (FROM SUBJECT)]'])
            # TODO use email.email.Utils.parseaddr() to break up the from for pretty printing
            msglst[uid] = {
                'uid': uid,
                'flags': m['FLAGS'],
                'subject': escape(msg['subject']),#escape(msubject, u''),
                'from': escape(msg['from']),#escape(mfrom,  u''),
                'date': m['INTERNALDATE'].strftime('%b %d %Y - %H:%M'),
                'size': m['RFC822.SIZE'],
            }
        except:
            # FIXME just ignoring for now (safe, but perhaps not as correct as it could
            # be), but we should likely retry or adjust the message list in the future
            pass
    
    imap.logout()

    return HttpResponse(json.dumps({'totalmsgs': nummsgs, 'start': start, 'stop': stop, 'msglist': msglst}))

@login_required
def viewmsg(request, server, folder, uid):
    """view message text
    
    :param request: request object from Django
    :param server: server number
    :param folder: which folder the message is in
    :param uid: the uid of the message to fetch
    """
    # these are here so they get passed through to the template
    folder = folder
    uid = int(uid)
    server = int(server)
    
    isrv = request.user.imap_servers.all()[server]
    i = imapclient.IMAPClient(isrv.address, port=isrv.port, use_uid=False, ssl=isrv.ssl)
    i.login(isrv.username, isrv.passwd)

    i.select_folder(folder)

    mailbody = i.fetch([uid], ['BODY', 'BODY[]'])
    mailstr = mailbody[uid]['BODY[]']
    if len(mailbody[uid]['BODY']) > 2 and mailbody[uid]['BODY'][2][1] == u'utf-8':
        mailstr = mailbody[uid]['BODY[]'].encode('ascii', 'replace')
    elif len(mailbody[uid]['BODY']) <= 2 and mailbody[uid]['BODY'][0][0][2][1] == u'utf-8':
        mailstr = mailbody[uid]['BODY[]'].encode('ascii', 'replace')
    mailmsg = email.message_from_string(mailstr.decode('quopri'))
    
    if not mailmsg.is_multipart():
        body = mailmsg.get_payload()
    else:
        for part in mailmsg.walk():
            if(part.get_content_type() == mailmsg.get_default_type()):
                body = part.get_payload().decode('quopri_codec')

    i.logout()
    
    if request.GET.get('json') == "true":
        return HttpResponse(json.dumps({'headers':mailmsg.items(), 'body':body}))

    return render(request, 'mail/viewmsg.html', {'mailmsg':mailmsg, 'body':body})

@login_required
def prefs(request):
    """preferences dialog
    
    :param request: request object from Django
    """
    from mail.forms import SmtpServerForm
    smtpform = SmtpServerForm(initial={'address':'localhost', 'port':'25'})
    return render_to_response('mail/config/prefs.html', locals(), context_instance=RequestContext(request))

@login_required
def newmail(request):
    """Compose new email dialog
    
    :param request: request object from Django
    """
    # TODO need to figure out what email addresses they are allowed to use as from:
    # TODO also change the whole sending email to use newforms
    # FIXME don't return a form if they don't have any smtp server setup
    return render_to_response('mail/newmail.html', locals(), context_instance=RequestContext(request))

@login_required
def send(request):
    """send an email from the browser and put a copy in Sent Messages
    
    :param request: request object from Django
    """
    from django.core.mail import send_mail, BadHeaderError#, EmailMultiAlternatives
    
    debug(request.user.smtp_servers.all(), request.user.imap_servers.all())
    
    ssrv = request.user.smtp_servers.all()[0] # FIXME which server?
    isrv = request.user.imap_servers.all()[0] # FIXME which server?

    # attempt to send the mail
    subject = request.POST.get('newmailsubject', '')
    message = request.POST.get('editor', '')
    mailfrom = request.POST.get('newmailfrom', '') # TODO should actually get their default from
    mailto = request.POST.get('newmailto', '')
    mailcc = request.POST.get('newmailcc', '')

    if request.POST.get('usingRTE') == "true":
        message = '<html><head></head><body>' + message + '</body></html>'

    emsg = email.mime.text.MIMEText(message)
    emsg['Subject'] = subject
    emsg['From'] = mailfrom
    emsg['To'] = mailto
    emsg['CC'] = mailcc
    emsg['User-Agent'] = 'Simone Webmail'
    emsg

    if subject and message and mailfrom and mailto:
        try:
            debug(request, request.user, request.user.smtp_servers, request.user.smtp_servers.all(), emsg, emsg.as_string())
            ss = smtplib.SMTP(host=ssrv.address, port=ssrv.port)
            ss.set_debuglevel(1)
            ss.starttls()
            ss.login(ssrv.username, ssrv.passwd)
            #ss.send_message(emsg) Python 3.2
            ss.sendmail(emsg.get('From'), emsg.get_all('To'), str(emsg))
            ss.quit()
            # FIXME handle html/multipart email
        except smtplib.SMTPAuthenticationError:
            return HttpResponse(json.dumps({'status':'ERROR', 'message': 'Invalid SMTP server settings'}))

        i = imapclient.IMAPClient(isrv.address, port=isrv.port, use_uid=False, ssl=isrv.ssl)
        i.login(isrv.username, isrv.passwd)

        i.select_folder('Sent')
        resp = i.append('Sent', str(emsg), [imapclient.SEEN])
        debug(resp)
        return HttpResponse(json.dumps({'status':'SUCCESS', 'message': 'Mail sent succesfully'})) # we can use short responses since we will only be submitting via ajax
    else:
        return HttpResponse(json.dumps({'status':'ERROR', 'message': 'Fill in all fields'+subject+message+mailfrom+mailto}))

@login_required
def config(request, action):
    """display form/change configuration settings, gets info from forms sent from browser
    
    :param request: request object from Django
    :param action: what action to do
    """
    from mail.forms import ImapServerForm, SmtpServerForm

    if action == "newconfig" or action == "newIMAPform":
        """display new IMAP form"""
        # we already know they don't have anything in the database, just show them a blank form
        iform = ImapServerForm(initial={'address':'localhost', 'port':'143'})
        srvtype = "IMAP"

    elif action == "newSMTPform":
        """display new SMTP form"""
        sform = SmtpServerForm(initial={'address':'localhost', 'port':'25'})
        srvtype = "SMTP"

    elif action == "addnew":
        """save new IMAP config"""
        if request.POST.get('newconfig') == "true":
            for srv in request.user.imap_servers.all():
                request.user.imap_servers.remove(srv)

        # we are adding some new configuration
        iform = ImapServerForm(request.POST)
        i = request.user.imap_servers.create(address=request.POST.get('address'),
                        port=request.POST.get('port'),
                        username=request.POST.get('username'),
                        passwd=request.POST.get('passwd'),
                        ssl=request.POST.get('ssl'))
        i.save()

        return HttpResponseRedirect('/mail/')

    elif action == "addnewsmtp":
        """save new SMTP config"""
        sform = SmtpServerForm(request.POST)
        s = request.user.smtp_servers.create(
                        address=request.POST.get('address'),
                        port=request.POST.get('port'),
                        username=request.POST.get('username'),
                        passwd=request.POST.get('passwd'))
        s.save()
        return HttpResponse(json.dumps({'status':'OK'}))

    elif action == "edit":
        """change existing settings from a form"""
        saction = request.GET.get('saction')
        srvtype = request.GET.get('srvtype')
        whichsrv = int(request.GET.get('which'))

        if saction == "REMOVE":
            srv = request.user.imap_servers.remove(request.user.imap_servers.all()[whichsrv])

        return HttpResponse(json.dumps({'status':'OK'}))
    else:
        """tbh, not even sure how this would get hit"""
        # default action / index
        imapsrvs = request.user.imap_servers.all()
        # the code below uses newforms, but these forms are so short it turned
        # out working better to just hand code them

    return render_to_response('mail/config/'+action+'.html', locals(),
        context_instance=RequestContext(request))

@login_required
def jsonview(request, action):
    """return data to the browser as json data

    :param request: request object from Django
    :param action: what data the browser requested
    """
    uprof = request.user

    if action == "folderlist2":
        # TODO order the folders in a more natural order
        server = int(request.GET['server'])
        srvr = uprof.imap_servers.all()[server]
        parent = ''
        if request.GET['parent']:
            parent = request.GET['parent'] + '.'

        imap = imapclient.IMAPClient(srvr.address, port=srvr.port, 
            use_uid=False, ssl=srvr.ssl)
        imap.login(srvr.username, srvr.passwd)
        flist = imap.list_folders(directory=parent, pattern='%')
        flist.reverse()
        imap.logout()
        
        jstreefolders = []
        for flags, delim, folder in flist:
            fd = {'ItemId':folder, 'Title':folder.split(delim)[-1]}
            if u'\\HasChildren' in flags:
                fd.update({'HasSubItem':True})
            jstreefolders.append(fd)

        # FIXME use list of subscribed folders
        return HttpResponse(json.dumps(jstreefolders))

    if action == "serverlist":
        srvlist = []
        i = 0
        for i, server in enumerate(uprof.imap_servers.all()):
            srvlist.append([i, server.address])
        return HttpResponse(json.dumps({'servers':srvlist}))
        
    if action == "unread":
        ret = {'servers': {
                '0': {
                    'INBOX': 500,
                    'Junk': 3,
                }
            }
        }
        server = int(request.POST['server'])
        folders = request.POST.getlist('folders[]')
        
        srvr = uprof.imap_servers.all()[server]
        imap = imapclient.IMAPClient(srvr.address, port=srvr.port, 
            use_uid=False, ssl=srvr.ssl)
        imap.login(srvr.username, srvr.passwd)

        for f in folders:
            resp = imap.select_folder(f)
            unread = len(imap.search(['UNSEEN',]))
            ret['servers']['0'][f] = unread

        imap.logout()
        return HttpResponse(json.dumps(ret))

@login_required
def action(request, action):
    """perform action on a message
    
    :param request: request object from Django
    :param action: what to do
    """
    # a few vars that get used in (almost) every action
    server = int(request.GET.get('server'))
    folder = request.GET.get('folder')

    # get the server
    try:
        my_imap_server = request.user.imap_servers.all()[server]
    except (IndexError, TypeError):
        return HttpResponse(json.dumps({'error':'Invalid server'}))

    server = imapclient.IMAPClient(my_imap_server.address, use_uid=False, ssl=my_imap_server.ssl)
    server.login(my_imap_server.username, my_imap_server.passwd)
    nummsgs = server.select_folder(folder)

    if 'uid' in request.GET:
        uids = [ request.GET['uid'] ]
    elif 'uids[]' in request.GET:
        uids = request.GET.getlist('uids[]')
    else:
        uids = request.GET.get('uid', '') # we've probably failed at life at this point
        
    debug('uids', uids, request.GET)

    rstat = "SUCCESS"
    rtext = "you suck at life"
    if action == 'markread':
        try:
            rtext = server.add_flags(uids, [imapclient.SEEN])
        except:
            rstat = 'FAILURE'
    elif action == 'markunread':
        try:
            rtext = server.remove_flags(uids, [imapclient.SEEN])
        except:
            rstat = 'FAILURE'
    elif action == 'markimportant':
        try:
            rtext = server.add_flags(uids, [imapclient.FLAGGED])
        except:
            rstat = 'FAILURE'
    elif action == 'markdeleted':
        try:
            rtext = server.delete_messages(uids)
        except:
            rstat = 'FAILURE'

    server.logout()

    return HttpResponse(json.dumps({'status':rstat, 'msg':rtext}))

def escape(s, quote=None):
    '''replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true, the quotation mark character (")
    is also translated.

    copied from python's cgi module and slightly
    massaged.'''
    
    from email.header import decode_header
    
    if s is None:
        return ""
    s, x = decode_header(s)[0]
    try:
        s = s.decode(x, "xmlcharrefreplace")
    except:
        pass
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s
