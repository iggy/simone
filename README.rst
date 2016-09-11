=============================
simone
=============================

.. image:: https://badge.fury.io/py/simone.png
    :target: https://badge.fury.io/py/simone

.. image:: https://travis-ci.org/iggy/simone.png?branch=master
    :target: https://travis-ci.org/iggy/simone

Simone :: Django Webmail

Documentation
-------------

The full documentation is at https://simone.readthedocs.org.

Quickstart
----------

Install simone::

    pip install simone

Then use it in a django project::

    INSTALLED_APPS = [
        ...
        'simone',
        ...
    ]

There is also a working minimal example that can be used via docker::

    make docker

Then point your browser at http://localhost:8000

There are some test accounts setup to get you going quicker. Use the example account to login and
setup you email servers. The admin account is there for emergencies and development.

    example:BiggerOnTheInside
    admin:WeepingAngels

Features
--------

* Reads email... not much else

Running Tests
--------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements_test.txt
    (myenv) $ python runtests.py

Credits
---------

Tools used in this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_
*  ImapClient_
*  jQuery_
*  jQueryUI_
*  JsonTree_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
.. _ImapClient: https://imapclient.readthedocs.io
.. _jQuery: https://jquery.com
.. _jQueryUI: https://jqueryui.com
.. _JsonTree: https://github.com/Erffun/JsonTree
