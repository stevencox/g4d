import logging
import json
from django.http import HttpResponse
from django.template import Context, loader
from django.template import RequestContext
logger = logging.getLogger (__name__)

class WebConstants:
    APP = "app"
    WORKFLOW = "workflow"
    TITLE = "title"
    USERNAME = "username"
    PASSWORD = "password"
    MESSAGE = "message"
    PATH = "path"
    IO_READ = "r"
    IO_WRITE = "w"
    MIME_HTML = "text/html"
    MIME_XML = "text/xml"
    MIME_TEXT = "text/plain"
    MIME_JSON = "application/json"

app_context = {}

class VUtil (object):
    @staticmethod
    def form_workflow_path (user, file_name=""):
        return ''

    @staticmethod
    def get_response (template,
                      request,
                      context = {},
                      mimeType = WebConstants.MIME_HTML,
                      status = 200):
        #context [WebConstants.APP] = app_context
        return HttpResponse (loader.
                             get_template ( template ).
                             render (RequestContext (request,
                                                     context)),
                             mimeType,
                             status,
                             mimeType)
    
    @staticmethod
    def get_text_response (text):
        return HttpResponse (text, WebConstants.MIME_TEXT, 200, WebConstants.MIME_TEXT)

    @staticmethod
    def get_json_response (response):
        text = ""
        if response:
            text = json.dumps (response, sort_keys=True, indent=2)
        return HttpResponse (text, WebConstants.MIME_JSON, 200, WebConstants.MIME_JSON)
