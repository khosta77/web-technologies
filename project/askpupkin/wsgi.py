"""
WSGI config for askpupkin project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'askpupkin.settings')

application = get_wsgi_application()
