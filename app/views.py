import json
import logging
import socket

from django.template import Context, loader
from django.conf import settings

from g4d.view.common import VUtil

logger = logging.getLogger (__name__)

def index (request):
    response = VUtil.get_response (template = 'app/index.html',
                                   request  = request,
                                   context  = {
            'fqdn' : socket.getfqdn ()
            })
    return response
