"""
WSGI config for summer_web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

sys.path.append('/home/ubuntu/miniconda3/envs/web/lib/python3.10/site-packages')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'summer_web.settings')

application = get_wsgi_application()
