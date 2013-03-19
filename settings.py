# Django settings for theiggy_com project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mail.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'mail.db'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Eastern'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = './media/'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
#MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '&5c4gyn8a!@*kpd#%36his9py!a6(bw)s-o(_!y%8+b0g9+cqk'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.doc.XViewMiddleware',
)

ROOT_URLCONF = 'django_webmail.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '../django_webmail/templates/',
)

#TEMPLATE_CONTEXT_PROCESSORS = (
#	'django.contrib.messages.context_processors.messages'
#)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
	#'django.contrib.messages',
	'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_webmail.mail',
    'django_webmail.person',
    #'django_extensions',
)

STATICFILES_DIRS = (
	'/var/www/django_webmail/media',
	'/usr/lib/python2.7/dist-packages/django/contrib/admin/static/admin',
)
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/django_webmail/static/'

AUTH_PROFILE_MODULE = 'person.UserProfile'

# LOGGING = {
    # 'version': 1,
    # 'disable_existing_loggers': False,
    # 'filters': {
        # 'require_debug_false': {
            # '()': 'django.utils.log.CallbackFilter',
            # 'callback': lambda r: not DEBUG
        # }
    # },
    # 'handlers': {
        # 'mail_admins': {
            # 'level': 'ERROR',
            # 'filters': ['require_debug_false'],
            # 'class': 'django.utils.log.AdminEmailHandler'
        # }
    # },
    # 'loggers': {
        # 'django.request': {
            # 'handlers': ['mail_admins'],
            # 'level': 'ERROR',
            # 'propagate': True,
        # },
    # }
# }

try:
    from local_settings import *
except ImportError, exp:
    pass

# Put the IMAP_SERVER setting into the local_settings.py file
