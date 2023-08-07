"""
WSGI config for AK_Graph_Backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AK_Graph_Backend.settings")

# load DB Pool
from neo4j_model.db_load import *

# load jieba
# from models.model_load import *

application = get_wsgi_application()
