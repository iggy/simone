# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import (
	ImapServer,
	SmtpServer,
)

from .forms import (
    ImapServerForm,
    SmtpServerForm,
)


class ImapServerCreateView(CreateView):

    model = ImapServer


class ImapServerDeleteView(DeleteView):

    model = ImapServer


class ImapServerDetailView(DetailView):

    model = ImapServer


class ImapServerUpdateView(UpdateView):

    model = ImapServer


class ImapServerListView(ListView):

    model = ImapServer


class SmtpServerCreateView(CreateView):

    model = SmtpServer


class SmtpServerDeleteView(DeleteView):

    model = SmtpServer


class SmtpServerDetailView(DetailView):

    model = SmtpServer


class SmtpServerUpdateView(UpdateView):

    model = SmtpServer


class SmtpServerListView(ListView):

    model = SmtpServer

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
    print(">>>>>>")
    for arg in args:
        pprint(arg)
    print("<<<<<<")

try:
    import imapclient
    import imaplib
    import ssl
except:
    print("imapclient module not available, please install it (pip install imapclient)")

@login_required
def index(request):
    """main index view

    :param request: request object from Django
    """
    # if they haven't filled in their options, we won't have much luck
    # connecting to their mail server
    try:
        if request.user.imapserver_set.all()[0].username == None:
            pass
    except:
        return HttpResponseRedirect('config/newconfig/')

    folder = "INBOX"

    # defaultEditor = request.user.editor

    srvr = request.user.imapserver_set.all()[0]
    try:
        sslcontext = imapclient.create_default_context()
        sslcontext.check_hostname = False
        # sslcontext.wrap_context
        sslcontext.verify_mode = ssl.CERT_OPTIONAL
        sslcontext.options |= ssl.OP_NO_SSLv2
        sslcontext.options |= ssl.OP_NO_SSLv3
        imap = imapclient.IMAPClient(srvr.address, port=srvr.port, use_uid=False, ssl=srvr.ssl, ssl_context=sslcontext)
        imap.login(srvr.username, srvr.passwd)
        folderlist = imap.list_folders()
        folderlist.reverse()
        imap.logout()
        return render(request, 'main.html', locals())
    except imaplib.IMAP4.error as imaperr:
        return HttpResponse('Error connecting to IMAP server: {}<br>{}'.format(srvr.address, imaperr))

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
    srvr = request.user.imapserver_set.all()[server]

    imap = imapclient.IMAPClient(srvr.address, port=srvr.port, use_uid=False, ssl=srvr.ssl)
    imap.login(srvr.username, srvr.passwd)
    folder_info = imap.select_folder(folder)

    if search == "":
        search = u'ALL'
    try:
        tofetch = imap.sort(['DATE', 'ARRIVAL'], search)
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
            debug('m', m)
            p = email.parser.BytesHeaderParser()

            msg = p.parsebytes(m[b'BODY[HEADER.FIELDS (FROM SUBJECT)]'], True)
            debug('msg', msg)
            fromlist = email.utils.parseaddr(msg['from'])
            if fromlist[0] == '':
                fromlist = [msg['from'], msg['from']]
            msglst[uid] = {
                'uid': uid,
                'flags': m[b'FLAGS'],
                'subject': escape(msg['subject']),  #escape(msubject, u''),
                'from': [escape(fromlist[0]), fromlist[1]],
                'date': m[b'INTERNALDATE'].strftime('%b %d %Y - %H:%M'),
                'size': m[b'RFC822.SIZE'],
            }
        except:
            # FIXME just ignoring for now (safe, but perhaps not as correct as it could
            # be), but we should likely retry or adjust the message list in the future
            debug(sys.exc_info())
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

    isrv = request.user.imapserver_set.all()[server]
    i = imapclient.IMAPClient(isrv.address, port=isrv.port, use_uid=False, ssl=isrv.ssl)
    i.login(isrv.username, isrv.passwd)

    i.select_folder(folder)

    p = email.parser.Parser()

    # BODY = metadata; BODY[] = the actual text of the body
    mailbody = i.fetch([uid], ['BODY', 'BODY[]'])
    debug(mailbody)
    mailstr = mailbody[uid]['BODY[]'].encode('ascii', 'ignore')
    if len(mailbody[uid]['BODY']) > 2 and mailbody[uid]['BODY'][2][1] == u'utf-8':
        mailstr = mailbody[uid]['BODY[]'].encode('ascii', 'ignore')
    elif len(mailbody[uid]['BODY']) <= 2 and mailbody[uid]['BODY'][0][0][2][1] == u'utf-8':
        mailstr = mailbody[uid]['BODY[]']
    mailmsg = p.parsestr(mailstr)

    if not mailmsg.is_multipart():
        body = mailmsg.get_payload(decode=True)
    else:
        for part in mailmsg.walk():
            if(part.get_content_type() == 'text/plain'):
                body = part.get_payload(decode=True)
                break # FIXME this assumes the first text/plain part is what we want
    if body == "":
        body = "There is no plain text version of this message."
        #body = body + "Raw Source:<br />" + mailmsg

    i.logout()

    if request.GET.get('json') == "true":
        return HttpResponse(json.dumps({'headers':mailmsg.items(), 'body':body}))

    data = {
        'mailmsg':mailmsg,
        'body':body,
        'folder': folder,
        'uid': uid,
        'server': server,
    }
    return render(request, 'mail/viewmsg.html', data)

@login_required
def prefs(request):
    """preferences dialog

    :param request: request object from Django
    """
    smtpform = SmtpServerForm(initial={'address':'localhost', 'port':'25'})
    return render(request, 'config_prefs.html', {'smtpform': smtpform})

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

    debug(request.user.smtpserver_set.all(), request.user.imapserver_set.all())

    ssrv = request.user.smtpserver_set.all()[0] # FIXME which server?
    isrv = request.user.imapserver_set.all()[0] # FIXME which server?

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
    #emsg

    if subject and message and mailfrom and mailto:
        try:
            debug(request, request.user, request.user.smtpserver_set, request.user.smtpserver_set.all(), emsg, emsg.as_string())
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
            for srv in request.user.imapserver_set.all():
                request.user.imapserver_set.remove(srv)

        # we are adding some new configuration
        iform = ImapServerForm(request.POST)
        i = request.user.imapserver_set.create(address=request.POST.get('address'),
                        port=request.POST.get('port'),
                        username=request.POST.get('username'),
                        passwd=request.POST.get('passwd'),
                        ssl=request.POST.get('ssl'))
        i.save()

        return HttpResponseRedirect('/mail/')

    elif action == "addnewsmtp":
        """save new SMTP config"""
        sform = SmtpServerForm(request.POST)
        s = request.user.smtpserver_set.create(
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
            srv = request.user.imapserver_set.remove(request.user.imapserver_set.all()[whichsrv])

        return HttpResponse(json.dumps({'status':'OK'}))
    else:
        """tbh, not even sure how this would get hit"""
        # default action / index
        imapsrvs = request.user.imapserver_set.all()
        # the code below uses newforms, but these forms are so short it turned
        # out working better to just hand code them

    return render(request, 'config_{}.html'.format(action), locals())

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
        srvr = uprof.imapserver_set.all()[server]
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
            fd = {
                'ItemId': folder,
                'Title': folder.split(str(delim))[-1],
            }
            if u'\\HasChildren' in flags:
                fd.update({'HasSubItem':True})
            jstreefolders.append(fd)

        # FIXME use list of subscribed folders
        return HttpResponse(json.dumps(jstreefolders))

    if action == "serverlist":
        srvlist = []
        i = 0
        for i, server in enumerate(uprof.imapserver_set.all()):
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

        srvr = uprof.imapserver_set.all()[server]
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
        my_imap_server = request.user.imapserver_set.all()[server]
    except (IndexError, TypeError):
        return HttpResponse(json.dumps({'error':'Invalid server'}))

    imap = imapclient.IMAPClient(my_imap_server.address, use_uid=False, ssl=my_imap_server.ssl)
    imap.login(my_imap_server.username, my_imap_server.passwd)
    nummsgs = imap.select_folder(folder)

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
            rtext = imap.add_flags(uids, [imapclient.SEEN])
        except:
            rstat = 'FAILURE'
    elif action == 'markunread':
        try:
            rtext = imap.remove_flags(uids, [imapclient.SEEN])
        except:
            rstat = 'FAILURE'
    elif action == 'markimportant':
        try:
            rtext = imap.add_flags(uids, [imapclient.FLAGGED])
        except:
            rstat = 'FAILURE'
    elif action == 'markdeleted':
        try:
            rtext = imap.delete_messages(uids)
            imap.expunge()
        except:
            rstat = 'FAILURE'
    elif action == 'mccopy':
        try:
            newfolder = request.GET.get('newfolder', 'INBOX') # should be a safe default
            rtext = imap.copy(uids, newfolder)
        except:
            rstat = 'FAILURE'
    elif action == 'mcmove':
        try:
            newfolder = request.GET.get('newfolder', 'INBOX') # should be a safe default
            debug(server, folder, newfolder, imap.capabilities())
            # RFC 6851 is supported by my server, but not by python's imaplib
            #if imap.has_capability(u'MOVE'):
            #    rtext = imap.move(uids, newfolder)
            #else:
            #    raise # I'm lazy, if their server doesn't support move, neither do we
            rtext1 = imap.copy(uids, newfolder)
            rtext2 = imap.delete_messages(uids)
            rtext3 = imap.expunge()
            rtext.extend(rtext1)
            rtext.extend(rtext2)
            rtext.extend(rtext3)
        except:
            rstat = 'FAILURE'


    imap.logout()

    return HttpResponse(json.dumps({'status':rstat, 'msg':rtext}))

def escape(s, quote=None):
    '''replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true, the quotation mark character (")
    is also translated.

    copied from python's cgi module and slightly
    massaged.'''

    if s is None:
        return ""
    try:
        s2, enc = email.Header.decode_header(s)[0]
        s = s2.decode(enc)
    except:
        pass # we don't really care if it fails, worst case users see weirdness
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
