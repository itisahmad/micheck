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

_application = get_wsgi_application()


def app(environ, start_response):
    """WSGI app: handle all requests and fix PATH_INFO for admin routes."""
    path = environ.get("PATH_INFO", "")
    
    # Handle static files (CSS, JS, images)
    if path.startswith("/staticfiles/") or path.startswith("/static/"):
        # Keep static routes as they are
        pass
    # Handle favicon
    elif path == "/favicon.ico":
        # Let Django handle favicon 404 gracefully
        pass
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
