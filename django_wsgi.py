import sys
import os
import django.core.handlers.wsgi

sys.path.append('/var/lib/django/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'marissa.settings'
application = django.core.handlers.wsgi.WSGIHandler()