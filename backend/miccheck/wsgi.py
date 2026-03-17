"""
WSGI config for miccheck project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miccheck.settings')

# Add WhiteNoise for static file serving
from whitenoise import WhiteNoise
application = get_wsgi_application()
application = WhiteNoise(application, root='staticfiles')

# For Vercel serverless compatibility
app = application