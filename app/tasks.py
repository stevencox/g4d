import logging

from celery.task import PeriodicTask
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache
from g4d.monitor.core import DAGDebug

dag_debug = DAGDebug ()

logger = logging.getLogger (__name__)

#http://stackoverflow.com/questions/8224482/examples-of-django-and-celery-periodic-tasks
class MonitordTask (PeriodicTask):
    run_every = timedelta (seconds=3)
    LOCK_EXPIRE = 60 * 60 * 5 # Lock expires in 5 hours

    def __init__(self):
        self.monitord_lock = 'monitord'
        cache.delete (self.monitord_lock)
        
    def acquire_lock (self):
        return cache.add (self.monitord_lock, "true", MonitordTask.LOCK_EXPIRE)

    def release_lock (self):
        cache.delete (self.monitord_lock)

    def run(self, **kwargs):
        monitord_lock = 'monitord'
        if self.acquire_lock ():
            logger.info ("++++> servicing %s %s", monitord_lock, cache.get (monitord_lock))
            flow_root = settings.FLOW_ROOT
            dag_debug.prepare (flow_root)
            dag_debug.monitor (flow_root)
            self.release_lock ()
        else:
            logger.info (".....already being serviced")

