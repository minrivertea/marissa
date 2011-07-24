import sys
import os
import django.core.handlers.wsgi

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'marissa.settings'
application = django.core.handlers.wsgi.WSGIHandler()