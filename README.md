simone
======

Django webmail package

to run locally:
$ cd /path/to/simone.git

create local_settings.py (at some point you will at least want SECRET_KEY set)

$ python2 manage.py syncdb --pythonpath=..
(go through the creating superuser process)

$ python2 manage.py runserver --pythonpath=..

Open up a browser and go to http://127.0.0.1:8000/admin
Add a new user to use
$ python2 manage.py changepassword *newuser* --pythonpath=..
Logout
Go to http://127.0.0.1/mail
Fill in your IMAP details
Profit!


What works:
reading email.... that's about it for now

Requirements:
django (1.6+)
python-simplejson (part of newer python's I think)
imapclient (pip install imapclient)
probably python-2.5

Icons are from kde4
src/KDE/kdebase/runtime/pics/oxygen

