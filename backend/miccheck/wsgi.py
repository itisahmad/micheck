"""
WSGI config for miccheck project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miccheck.settings')
application = get_wsgi_application()
app = application