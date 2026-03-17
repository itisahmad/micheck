"""
Vercel serverless entry: expose Django WSGI app.
All /api/* and /admin/* requests are handled by this app.
"""
import os
import sys

# Ensure project root (backend) is on path when deployed (root dir = backend)
_backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miccheck.settings")

from django.core.wsgi import get_wsgi_application
from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler

_application = get_wsgi_application()


def app(environ, start_response):
    """WSGI app: handle all requests and fix PATH_INFO for admin routes."""
    path = environ.get("PATH_INFO", "")
    
    # For static files, we need to serve them directly
    if path.startswith("/static/") or path.startswith("/staticfiles/"):
        # Use Django's static file serving
        from django.contrib.staticfiles.handlers import StaticFilesHandler
        static_app = StaticFilesHandler(_application)
        return static_app(environ, start_response)
    # Handle favicon
    elif path == "/favicon.ico":
        # Try to serve favicon or return 404
        try:
            from django.contrib.staticfiles.handlers import StaticFilesHandler
            static_app = StaticFilesHandler(_application)
            return static_app(environ, start_response)
        except:
            start_response("404 Not Found", [])
            return [b""]
    # Handle admin routes directly - don't redirect to /api/
    elif path.startswith("/admin"):
        # Keep admin routes as they are
        pass
    # Handle health check
    elif path == "/health" or path == "/":
        environ["PATH_INFO"] = "/api/"
    # Handle API routes
    elif path.startswith("/api/"):
        # Keep /api/ routes as they are
        pass
    else:
        # For any other path, redirect to /api/
        environ["PATH_INFO"] = "/api/" + path.lstrip("/")
    
    return _application(environ, start_response)
