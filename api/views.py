import json
import logging
from django.template import Context, loader
from django.conf import settings

from g4d.view.common import VUtil
from g4d.monitor.core import DebugAPI

'''
http://localhost:8080/api/workflows
http://localhost:8080/api/jobs?workflow=one/07a49762-2f1e-41e9-ae50-0220e842031a/HelloWorld.stampede.db
http://localhost:8080/api/job_instances?workflow=one/07a49762-2f1e-41e9-ae50-0220e842031a/HelloWorld.stampede.db&job_id=1
http://localhost:8080/api/submitfile?file=one/07a49762-2f1e-41e9-ae50-0220e842031a/CatCLI_3.sub
http://localhost:8080/api/dagman?file=one/07a49762-2f1e-41e9-ae50-0220e842031a/*.dag
http://localhost:8080/api/dagmanout?file=one/07a49762-2f1e-41e9-ae50-0220e842031a/*.dagman.out
http://localhost:8080/api/dagmanout?file=one/07a49762-2f1e-41e9-ae50-0220e842031a/*xml
'''

logger = logging.getLogger (__name__)

debugAPI = DebugAPI (settings.FLOW_ROOT)

def workflows (pag = None):
    return VUtil.get_json_response ({
            'flows' : debugAPI.get_workflows ()
            })

def jobs (request, pag = None):
    workflow = request.REQUEST ['workflow'] 
    return VUtil.get_json_response ({
            'jobs' : debugAPI.get_jobs (workflow)
            })
 
def job_instances (request, pag = None):
    workflow = request.REQUEST ['workflow'] 
    job_id = request.REQUEST ['job_id']
    return VUtil.get_json_response ({
            'job_instances' : debugAPI.get_job_instances (workflow, job_id)
            })
    
def get_file (request, pattern = False, tag = 'file', pag = None):
    file_name = request.REQUEST ['file']
    if 'pattern' in request.REQUEST:
        pattern = request.REQUEST ['pattern']

    return VUtil.get_json_response ({
            tag : debugAPI.get_file (file_name, pattern)
            })

def submitfile (request, pag = None):
    return get_file (request, tag = 'submitfile')
def dagman (request, pag = None):
    return get_file (request, pattern = True, tag = 'dagman')
def dagmanout (request, pag = None):
    return get_file (request, pattern = True, tag = 'dagmanout')
    
