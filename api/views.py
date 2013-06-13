import json
import logging

from django.conf import settings
from django.template import Context, loader
from g4d.monitor.core import DebugAPI
from g4d.view.common import VUtil
from g4d.model.mongo import MongoModel

mongo = MongoModel ()

logger = logging.getLogger (__name__)

debugAPI = DebugAPI (settings.FLOW_ROOT)

def flows (request, name_filter = None, status_filter = None, pag = None):
    return VUtil.get_json_response ({
            'flows' : debugAPI.get_workflows (name_filter, status_filter)
            })

def jobs (request, flow, pag = None):
    return VUtil.get_json_response ({
            'jobs' : debugAPI.get_jobs (flow)
            })
 
def job_instances (request, pag = None):
    workflow = request.REQUEST ['workflow'] 
    job_id = request.REQUEST ['job_id']
    return VUtil.get_json_response ({
            'job_instances' : debugAPI.get_job_instances (workflow, job_id)
            })
    
def get_file (request, pattern, page, tag):
    return VUtil.get_json_response ({
            'file' : debugAPI.get_file (tag, pattern)
            })

def add_flow (request, flow_name):
    return VUtil.get_json_response ({
            'fid' : str (mongo.add_flow (flow_name))
            })

def list_flows (request, current_id, target_page, page_size):
    return VUtil.get_json_response ({
            'flows' : mongo.list_flows (current_id, int(target_page), int(page_size))
            })
