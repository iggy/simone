# Create your views here.
import email, quopri
from pprint import pprint

from django.shortcuts import render_to_response, HttpResponse
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

import json as simplejson

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
    debug("args:", server, folder, page, perpage, sortc, sortdir, search)
    server = int(server)
    srvr = request.user.imap_servers.all()[server]
    #pprint(srvr)

    imap = imapclient.IMAPClient(srvr.address, port=srvr.port, use_uid=False, ssl=srvr.ssl)
    imap.login(srvr.username, srvr.passwd)
    debug(s)
    folder_info = imap.select_folder(folder)
    debug(folder_info)
    
    if search == "":
        search = u'ALL'
    tofetch = imap.sort("ARRIVAL", search)
    
    nummsgs = len(tofetch)
    
    start = int(page) * int(perpage) - int(perpage) + 1
    stop = int(page) * int(perpage)

    if stop > nummsgs:
        stop = nummsgs
    
    debug(start, stop, sortdir)
    if sortdir == u'D':
        start = nummsgs - int(page) * int(perpage)
        stop = nummsgs - int(int(page) - 1) * int(perpage)
    debug(start, stop)
    
    # we just need the headers for the msglist
    msglst = {}
    
    fetched = imap.fetch(tofetch[start:stop], ['UID', 'FLAGS', 'INTERNALDATE', 'BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)]', 'RFC822.SIZE'])
    
    for uid in fetched:
        try:
            m = fetched[uid]
            msg = email.message_from_string(m['BODY[HEADER.FIELDS (FROM SUBJECT)]'])
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

    return HttpResponse(simplejson.dumps({'totalmsgs': nummsgs, 'start': start, 'stop': stop, 'msglist': msglst}))
    #return HttpResponse(simplejson.dumps({'totalmsgs': len(msglst), 'start': start, 'stop': stop, 'msglist': msglst}))

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
    debug(mailbody[uid]['BODY'], len(mailbody[uid]['BODY']))
    if len(mailbody[uid]['BODY']) > 2 and mailbody[uid]['BODY'][2][1] == u'utf-8':
        mailstr = mailbody[uid]['BODY[]'].encode('ascii', 'replace')
    elif len(mailbody[uid]['BODY']) <= 2 and mailbody[uid]['BODY'][0][0][2][1] == u'utf-8':
        mailstr = mailbody[uid]['BODY[]'].encode('ascii', 'replace')
    mailmsg = email.message_from_string(mailstr.decode('quopri'))
    
    debug(folder, uid, folder)

    if not mailmsg.is_multipart():
        body = mailmsg.get_payload()
    else:
        for part in mailmsg.walk():
            if(part.get_content_type() == mailmsg.get_default_type()):
                body = part.get_payload().decode('quopri_codec')

    i.logout()
    debug(body)
    
    if request.GET.get('json') == "true":
        return HttpResponse(simplejson.dumps({'headers':mailmsg.items(), 'body':body}))

    return render_to_response('mail/viewmsg.html', locals())

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
    return render_to_response('mail/newmail.html', locals(), context_instance=RequestContext(request))

@login_required
def send(request):
    """send an email from the browser
    
    :param request: request object from Django
    """
    from django.core.mail import send_mail, BadHeaderError#, EmailMultiAlternatives
    from smtplib import SMTPAuthenticationError

    # attempt to send the mail
    subject = request.POST.get('newmailsubject', '')
    message = request.POST.get('editor', '')
    mailfrom = request.POST.get('newmailfrom', '') # TODO should actually get their default from
    mailto = request.POST.get('newmailto', '')

    if request.POST.get('usingRTE') == "true":
        message = '<html><head></head>' + message + '</html>'

    if subject and message and mailfrom and mailto:
        try:
            debug(request, request.user, request.user.smtp_servers, request.user.smtp_servers.all())
            send_mail(subject, message, mailfrom, [mailto], 
                auth_user=request.user.smtp_servers.all()[0].username, 
                auth_password=request.user.smtp_servers.all()[0].passwd)
            # FIXME send plain text part as well as html part
            #msg = EmailMultiAlternatives(subject, message, mailfrom, [mailto])
            #if request.POST.get('usingRTE') == "true":
                #msg.content_subtype = "html"
            #msg.send(auth_user=request.user, auth_password=request.user.smtp_servers.all()[0].passwd)
        except BadHeaderError:
            return HttpResponse(simplejson.dumps({'status':'ERROR', 'message': 'Invalid Header Found'}))
        except SMTPAuthenticationError:
            return HttpResponse(simplejson.dumps({'status':'ERROR', 'message': 'Invalid SMTP server settings'}))
        return HttpResponse(simplejson.dumps({'status':'SUCCESS', 'message': 'Mail sent succesfully'})) # we can use short responses since we will only be submitting via ajax
    else:
        return HttpResponse(simplejson.dumps({'status':'ERROR', 'message': 'Fill in all fields'+subject+message+mailfrom+mailto}))

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
        return HttpResponse(simplejson.dumps({'status':'OK'}))

    elif action == "edit":
        """change existing settings from a form"""
        saction = request.GET.get('saction')
        srvtype = request.GET.get('srvtype')
        whichsrv = int(request.GET.get('which'))

        if saction == "REMOVE":
            srv = request.user.imap_servers.remove(request.user.imap_servers.all()[whichsrv])

        return HttpResponse(simplejson.dumps({'status':'OK'}))
    else:
        """tbh, not even sure how this would get hit"""
        # default action / index
        imapsrvs = request.user.imap_servers.all()
        # the code below uses newforms, but these forms are so short it turned
        # out working better to just hand code them

    return render_to_response('mail/config/'+action+'.html', locals(),
        context_instance=RequestContext(request))

@login_required
def json(request, action):
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
        
        debug(flist)
        jstreefolders = []
        for flags, delim, folder in flist:
            #debug(flags, delim, folder)
            fd = {'ItemId':folder, 'Title':folder.split(delim)[-1]}
            if u'\\HasChildren' in flags:
                fd.update({'HasSubItem':True})
            #debug(fd)
            jstreefolders.append(fd)

        #debug(jstreefolders)
        
        # FIXME use list of subscribed folders
        return HttpResponse(simplejson.dumps(jstreefolders))

    if action == "serverlist":
        srvlist = []
        i = 0
        for i, server in enumerate(uprof.imap_servers.all()):
            srvlist.append([i, server.address])
        return HttpResponse(simplejson.dumps({'servers':srvlist}))

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
        return HttpResponse(simplejson.dumps({'error':'Invalid server'}))

    server = imapclient.IMAPClient(my_imap_server.address, use_uid=False, ssl=my_imap_server.ssl)
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
    elif action == 'markdeleted':
        try:
            uid = request.GET.get('uid')
            rtext = server.delete_messages([uid])
        except:
            rstat = 'FAILURE'


    return HttpResponse(simplejson.dumps({'status':rstat, 'msg':rtext}))

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
