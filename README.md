simone
======

Questions? Answers? General thoughts?

  #simone @ irc.oftc.net

Django webmail package

to run locally:
* make sure requirements are installed (See below)
* $ cd /path/to/simone.git
* create local_settings.py (at some point you will at least want SECRET_KEY set)
* $ python2 manage.py syncdb --pythonpath=..
(go through the creating superuser process)
* $ python2 manage.py runserver --pythonpath=..
* Open up a browser and go to http://127.0.0.1:8000/admin
* Add a new user to use
* $ python2 manage.py changepassword --pythonpath=.. *newuser*
* In your browser, logout
* Go to http://127.0.0.1:8000/mail
* Fill in your IMAP details
* Profit!


What works:

reading email.... that's about it for now

Requirements:
* django (1.6+)
* imapclient (pip install imapclient)
* probably python-2.7 (it's all I've tested, theoretically 2.6+ should work)

(NOTE: do not intall imaplib2)

Uses:
jQuery
jQueryUI (including the overcast theme)
JsonTree (https://github.com/Erffun/JsonTree)
