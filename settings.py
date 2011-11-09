# Django settings for Marissa project.

import os
PROJECT_PATH = os.path.normpath(os.path.dirname(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False


ADMINS = (
    ('Chris West', 'chris@minrivertea.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

TIME_ZONE = 'Europe/London'

LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

ADMIN_MEDIA_PREFIX = '/admin/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '12345'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
#    'ab.loaders.load_template_source',
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'marissa.shop.context_processors.get_basket',
    'marissa.shop.context_processors.get_basket_quantity',
#    'marissa.shop.context_processors.get_shopper',
    'marissa.shop.context_processors.common',
    'marissa.shop.context_processors.get_products',
    'marissa.shop.context_processors.get_categories',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
#    'ab.middleware.ABMiddleware',
)

AUTHENTICATION_BACKENDS = (
    "emailauth.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
)


ROOT_URLCONF = 'marissa.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, "templates/")
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
#    'django.contrib.flatpages',
    'django.contrib.sitemaps',
    'django.contrib.comments',
    'shop',
    'blog',
    'sorl.thumbnail',
    'paypal.standard.ipn',
    'django_static',
    'registration',
#    'ab',
)

# Random app information for different things
GA_IS_ON = False
PROJECT_NAME = 'WeSourceFactories'
PROJECT_EMAIL = 'sales@wesourcefactories.com'
ADMIN_EMAIL = 'sales@wesourcefactories.com'
PROJECT_URL = 'http://www.wesourcefactories.com'
SHIPPING_PRICE = '3'
PAYMENTS_ACTIVE = False
AUTH_PROFILE_MODULE = "shop.Shopper"

# tinymce stuff
TINYMCE_JS_URL = "js/tiny_mce/tiny_mce.js"
TINYMCE_JS_ROOT = "js/tiny_mce"
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,paste,searchreplace",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
}


# django-static info
DJANGO_STATIC = True
DJANGO_STATIC_SAVE_PREFIX = '/tmp/cache-forever'
DJANGO_STATIC_NAME_PREFIX = '/cache-forever'
# DJANGO_STATIC_MEDIA_URL = 'http://static.minrivertea.com'

# mail settings
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = ''
SITE_EMAIL = 'info@whatever.com'

# paypal info
PAYPAL_IDENTITY_TOKEN = ""
PAYPAL_RECEIVER_EMAIL = ''
PAYPAL_RETURN_URL = ''
PAYPAL_NOTIFY_URL = ''
PAYPAL_BUSINESS_NAME = ''
PAYPAL_SUBMIT_URL = 'https://www.paypal.com/cgi-bin/webscr'




LOG_FILENAME = ""

try:
    from local_settings import *
except ImportError:
    pass
    
try:
    from filebrowser.settings.py import *
except ImportError:
    pass

import logging 
                    
logging.basicConfig(filename=LOG_FILENAME,
                   level=logging.DEBUG,
                   datefmt="%Y-%m-%d %H:%M:%S",
                   format="%(asctime)s %(levelname)s %(name)s %(message)s",
                  )
