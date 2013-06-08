#!/usr/bin/env python

import re
import glob
import string
import os
import sys
import argparse
import logging
import fnmatch 
import string
import sqlite3
import json 

from datetime import datetime

logger = logging.getLogger (__name__)

class Util (object):
    ''' General system utilities '''

    def get_file_as_dict (self, file_name):
        d = {}
        with open (file_name) as f:
            for line in f:
                line = line.strip ()
                if '=' in line:
                    (key, val) = string.split (line, sep = '=', maxsplit = 1)
                    d [key.strip ()] = val.strip ()
        return d

    def get_timestamp (self):
        return datetime.now ().strftime ("%FT%H:%M:%SZ")

    def rm_all (self, dirname, pattern):
        #logger.debug ("rm_all: %s %s", dirname, pattern)
        file_pattern = os.path.join (dirname, pattern)
        for file_name in glob.glob (file_pattern):
            logger.info ("  --Removing %s", file_name)
            #os.remove (file_name)
    
    def write_json (self, obj, file_name, preamble = ''):
        with open (file_name, 'w') as stream:
            stream.write (preamble)
            stream.write (json.dumps (obj, indent = 2, sort_keys = True))

    def read_file (self, file_name, path_prefix = None, pattern = False):
        text = None
        if path_prefix:
            file_name = os.path.join (path_prefix, file_name)

        if pattern:
            file_name = glob.glob (file_name)[0]

        with open (file_name, 'r') as stream:
            text = stream.read ()
        return text

class DebugAPI (object):

    def __init__(self, directory):
        self.directory = directory
        self.u = Util ()

    def get_db (self, flow):
        db_path = os.path.join (self.directory, flow)
        return StampedeDB (db_path)

    def get_workflows (self):
        workflows = []
        for root, dirnames, filenames in os.walk (self.directory):
            for idx, file_name in enumerate (fnmatch.filter (filenames, '*.stampede.db')):
                full_path = os.path.join (root, file_name)
                exit_code, exit_status = self.get_dag_exitcode (os.path.dirname (full_path))
                full_path = full_path.replace (self.directory, '')
                logger.error (full_path)
                #workflow_dir = os.path.dirname (full_path)
                workflow_name = full_path.replace ('.stampede.db', '') 
                workflows.append ({
                        'name'        : workflow_name, #workflow_dir,
                        'full_path'   : full_path,
                        'exit_code'   : exit_code,
                        'exit_status' : exit_status
                        })
        return workflows

    def get_job_details (self, path, job):
        result = None
        print job
        job_name = job ['exec_job_id']
        pat_submit  = re.compile ('^(\d+) {0} SUBMIT (\d+.\d+).*$'.format (job_name))
        pat_execute = re.compile ('^(\d+) {0} EXECUTE.*$'.format (job_name))
        pat_success = re.compile ('^(\d+) {0} JOB_SUCCESS .*$'.format (job_name))
        pat_failure = re.compile ('^(\d+) {0} JOB_FAILURE.*$'.format (job_name))
        path = os.path.join (self.directory, path)
        path = os.path.join (path, 'output')
        jobstatus = os.path.join (path, '*-jobstate.log')
        stats = glob.glob (jobstatus)
        if len (stats) > 0:
            with open (stats[0], 'r') as stream:
                for line in stream:
                    print line
                    match = pat_submit.match (line)
                    if match:
                        job ['status'] = 'submitted'
                        job ['submit_timestamp'] = match.group (1)
                        job ['schedd_id'] = match.group (2)
                    else:
                        match = pat_execute.match (line)
                        if match:
                            job ['status'] = 'running'
                        else:
                            match = pat_success.match (line)
                            if match:
                                job ['status'] = 'succeeded'
                            else:
                                match = pat_failure.match (line)
                                if match:
                                    job ['status'] = 'failed'

    def get_dag_exitcode (self, path):
        result = None
        result_code = None
        pat_finished = re.compile ('^.*DAGMAN_FINISHED (\d+).*$')
        pat_sigterm = re.compile ('^.*SIGTERM\. .*$')
        path = os.path.join (path, 'output')
        jobstatus = os.path.join (path, '*-jobstate.log')
        stats = glob.glob (jobstatus)
        if len (stats) > 0:
            with open (stats[0], 'r') as stream:
                for line in stream:
                    match = pat_finished.match (line)
                    if match:
                        result = int (match.group (1))
                    else:
                        match = pat_sigterm.match (line)
                        if match:
                            result = -100
        if result == 0:
            result_status = 'succeeded'
        elif result > 0:
            result_status = 'failed'
        elif result == -100:
            result_status = 'terminated'
        else:
            result_status = 'running'

        return result, result_status

    def get_jobs (self, flow):
        db = self.get_db (flow)
        jobs = db.write_table ('job')
        #jobs = table ['jobs']
        for job in jobs:
            self.get_job_details (os.path.dirname (flow), job)
        return jobs #table

    def get_job_instances (self, flow, job_id):
        db = self.get_db (flow)
        return db.write_table ('job_instance')

    def get_submit_file (self, submit_file):
        return self.u.read_file (submit_file, self.directory)

    def get_dagman (self, dag_name):
        return self.u.read_file (dag_name, self.directory, pattern = True)
        
    def get_file (self, file_name, pattern = False):
        if file_name.startswith ('/'):
            file_name = file_name [1:]
        text = None
        try:
            text = self.u.read_file (file_name, self.directory, pattern = pattern)
        except IndexError as e:
            text = 'ERROR file does not exist ({0})'.format (file_name)
        except (OSError, IOError) as e:
            text = 'ERROR reading {0}'.format (file_name) 
        return text;

        
class StampedeDB (object):

    def __init__ (self, database):
        self.con = sqlite3.connect (database)
        self.cur = self.con.cursor ()

    def run (self):
        all_recs = {}
        table_names = [ 'workflow', 'workflowstate', 'job', 'job_instance', 'task', 'task_edge', 'schema_info', 'job', 'invocation', 'host', 'file' ]
        for table_name in table_names:
            all_recs [table_name] = self.write_table (table_name)            
        print json.dumps (all_recs, indent = 2, sort_keys = True)

    def write_table (self, table_name):
        records = []
        rows = self.cur.execute ("select * from {0}".format (table_name)).fetchall ()
        for row in rows:
            obj = {}

            col_names = list (map (lambda x: x[0], self.cur.description))

            col_id = 0
            for col_name in col_names:
                obj [col_name] = row [col_id]
                col_id += 1

            records.append (obj)
        return records

class StatBP (object):
    ''' Manages Pegasus static.bp workflow representation files '''
    def __init__ (self, dag):
        self.u = Util ()
        self.dag = dag
        logger.info ("statbp: %s", self.dag)
        self.wf = self.dag.replace ('.dag', '')
        self.task = []
        self.task_edge = []
        self.job = []
        self.job_edge = []
        self.job_map = []        
            
        self.task_text = ''.join ([ 'ts={0} event=task.info xwf.id={1} task.id="{2}" type="1" ',
                                    'type_desc="compute" transformation="{3}::{2}:1.0" argv=""' ])
        
        self.job_text = ''.join ([ 'ts={0} event=job.info xwf.id={1} job.id="{2}" type="1" submit_file="{3}" ',
                                   'type_desc="compute" clustered="0" max_retries="3" ',
                                   'executable="{4}" argv="{5}" task_count="0"' ])
        
        self.map_text = 'ts={0} event=wf.map.task_job xwf.id={1} job.id="{2}" task.id="{3}"'
            
        self.task_edge_text = 'ts={0} event=task.edge xwf.id={1} parent.task.id="{2}" child.task.id="{3}"'
        
        self.job_edge_text = 'ts={0} event=job.edge  xwf.id={1} parent.job.id="{2}" child.job.id="{3}"'
        
    def form_task_id (self, job_id):
        return "{0}{1}".format (job_id, "Task")

    def emit_job_info (self, wf_uuid, job_id, properties):
        task_id = self.form_task_id (job_id)
        self.task.append (self.task_text.format (self.u.get_timestamp (), wf_uuid, task_id, self.wf))
        self.job.append (self.job_text.format (self.u.get_timestamp (), wf_uuid, job_id,
                                               properties ['submit_file'],
                                               properties ['executable'],
                                               '')) #properties ['arguments']))
        self.job_map.append (self.map_text.format (self.u.get_timestamp (), wf_uuid, job_id, task_id))

    def emit_edge_info (self, wf_uuid, parent_job_id, child_job_id):
        self.task_edge.append (self.task_edge_text.format (self.u.get_timestamp (), wf_uuid, 
                                                           self.form_task_id (parent_job_id),
                                                           self.form_task_id (child_job_id)))
        self.job_edge.append (self.job_edge_text.format (self.u.get_timestamp (), wf_uuid,
                                                         parent_job_id,
                                                         child_job_id))
    def write (self):
        output_file = self.dag.replace (".dag", ".static.bp")
        logger.info ("Writing statbp: %s", output_file)
        with open (output_file, 'w') as stream:
            for section in [ self.task, self.task_edge, self.job, self.job_map, self.job_edge ]:                    
                for line in section:
                    stream.write ('{0}\n'.format (line))

class DAGParser (object):
    ''' Parses DAGMan files '''
    def __init__(self, dag, dagdir):
        self.dag = dag
        self.dagdir = dagdir

    def parse (self, job_cb=None, parent_cb=None, retry_cb=None, subdag_cb=None):
        jobs = {}
        dagpath = os.path.join (self.dagdir, self.dag)
        with open (dagpath, 'r') as stream:
            for line in stream:
                elem = line.split ()
                if len (elem) == 0:
                    continue
                command = elem [0]
                if command == 'JOB':
                    job_id = elem [1]
                    submitfile = elem [2]
                    if job_cb:
                        job_cb (job_id, submitfile)
                elif command == 'PARENT':
                    parent_job = elem [1]
                    child_job = elem [3]
                    if parent_cb:
                        parent_cb (parent_job, child_job)
        return jobs

class Job (object):
    ''' Represents a job '''
    def __init__ (self, name, submitfile, dagdir, instance=None):
        self.u = Util ()
        self.sub = submitfile
        self.name = name
        self.dagdir = dagdir
        input = os.path.join (dagdir, submitfile)
        self.properties = self.u.get_file_as_dict (input)
        self.instance = instance

    def format_instance (self, file_name):
        return "{0}.{1}".format (output, self.instance) if self.instance else file_name

    def get_meta (self):
        output = self.format_instance (os.path.basename (self.properties ['output']))
        error = self.format_instance (os.path.basename (self.properties ['error']))
        return {
            'name'   : self.name,
            'sub'    : self.sub,
            'output' : output,
            'error'  : error
            }

class DAGDebug (object):
    ''' Bridge between raw DAGMan and Pegasus STAMPEDE '''
    def __init__(self):
        self.u = Util ()

    def prepare (self, dir_name):
        for root, dirnames, filenames in os.walk (dir_name):
            for idx, file_name in enumerate (fnmatch.filter (filenames, '*.dag')):
                dag_file = os.path.join (root, file_name)
                dagdir = os.path.dirname (dag_file)        
                self.write_statbp (dag_file)
                self.write_braindump (dag_file)
                self.write_properties (dag_file, dagdir)
                dirname = os.path.dirname (dag_file)
                self.u.rm_all (dirname, "*.stampede.db")
                self.u.rm_all (os.path.join (dirname, 'output'), "*-monitord.info")

                input_dag = []
                normalized_dag = []
                with open (dag_file, 'r') as stream:
                    for line in stream:
                        input_dag.append (line)
                        normalized_line = ' '.join (line.split ())
                        normalized_dag.append (normalized_line)
                        #logger.debug ("normalized line: %s", normalized_line)

                incoming_text = '\n'.join (input_dag)
                outbound_text = '\n'.join (normalized_dag)

                if incoming_text != outbound_text:
                    #logger.debug ("in< %s", incoming_text)
                    #logger.debug ("out> %s", outbound_text)
                    os.rename (dag_file, '%s.orig' % dag_file)
                    with open (dag_file, 'w') as stream:
                        stream.write (outbound_text)


    def write_statbp (self, dag):
        dagdir = os.path.dirname (dag)
        wf_uuid = os.path.basename (dagdir)    
        statbp = StatBP (dag)
        dag = os.path.basename (dag)
        parser = DAGParser (dag, dagdir)
        def job_cb (job_id, submitfile):
            sub_file = os.path.join (dagdir, submitfile)
            submit_properties = self.u.get_file_as_dict (sub_file)
            submit_properties ['submit_file'] = submitfile
            statbp.emit_job_info (wf_uuid, job_id, submit_properties)
        def parent_cb (parent_job_id, child_job_id):
            statbp.emit_edge_info (wf_uuid, parent_job_id, child_job_id)
        parser.parse (job_cb, parent_cb)
        statbp.write ()
    
    def write_properties (self, dag, dagdir):
        dag_name = os.path.basename (dag).replace ('.dag', '')
        properties_file = os.path.join (dagdir, "pegasus.properties")
        wf_uuid = os.path.basename (dagdir)
        with open (properties_file, 'w') as stream:
            stream.write ("pegasus.workflow.root.uuid={0}-{1}\n".format (dag_name, wf_uuid))

    def write_braindump (self, dag):
        dirname = os.path.abspath (os.path.normpath (os.path.dirname (dag)))
        braindump = os.path.join (dirname, 'braindump.txt')
        logger.info ("Writing braindump: %s", braindump)
        braindump_text = \
"""\
dax {1}.dax
dax_label {1}-{0}
dax_index 0
dax_version 1.0
wf_uuid {0}
dag {1}
submit_dir {2}
planner_arguments ""
user {3}
"""
        with open (braindump, "w") as stream:
            wf_uuid = os.path.basename (os.path.dirname (dag))
            user = os.environ ['USER']
            stream.write (braindump_text.format (wf_uuid, os.path.basename (dag).replace ('.dag', ''), dirname, user))

    def monitor (self):
        for root, dirnames, filenames in os.walk ("."):
            for idx, dagmanout in enumerate (fnmatch.filter (filenames, '*.dagman.out')):
                logger.info ("Scanning %s @ %s", dagmanout, root)
                dagdir = root
                output = os.path.join (dagdir, 'output')
                if not os.path.exists (output):
                    os.makedirs (output)
                curdir = os.getcwd ()
                os.chdir (dagdir)


                logger.error("-----------------> %s" % os.getcwd ())
                command = 'pegasus-monitord {0} {1} --conf=pegasus.properties --no-daemon --db-stats --output-dir=output --no-notifications'
                #command = 'pegasus-monitord {0} {1} --conf=pegasus.properties --db-stats --output-dir=output --no-notifications'
                command = command.format (dagmanout, '-v -v -v -v')
                logger.info ("Running %s", command)
                os.system (command)
                os.chdir (curdir)

    def write_output (self):
        dagmetas = []
        for root, dirnames, filenames in os.walk ("."):
            for idx, jobstate_log in enumerate (fnmatch.filter (filenames, '*-jobstate.log')):
                logger.info ("write-output: Scanning %s @ %s", jobstate_log, root)
                dagdir = os.path.dirname (root)
                dag_p = os.path.join (dagdir, '*.dag')
                dag = os.path.basename (glob.glob (dag_p)[0])
                dagout = '{0}.dagman.out'.format (dag)
                logger.info ('dagdir: %s %s', dagdir, dag)
                
                jobs = {}
                parser = DAGParser (dag, dagdir)
                def job_cb (job_id, submitfile):
                    jobs [job_id] = Job (job_id, submitfile, dagdir)
                parser.parse (job_cb)

                database_pattern = os.path.join (dagdir, "*stampede.db")
                databases = glob.glob (database_pattern)
                if len (databases) > 0:
                    database = databases [0]
                    logger.debug ("Exporting stampede database: %s", database)
                    exporter = StampedeDB (database)
                    exporter.run ()

                '''
                job_runs = []
                versioned_files = os.path.join (dagdir, '*.000')
                has_multiple_runs = glob.glob (versioned_files)
                if len (has_multiple_runs) > 0:
                    for instance_num in range (0, 100):
                        instance_tag = "{0}".format (instance_num).zfill (3)
                        for job_key in jobs:
                            job = jobs [job_key]
                            out_file = os.path.join (dagdir, job ['output'])
                            if os.path.exists (out_file):
                                pass
                                '''

                dagmetas.append (self.get_dagmeta (dag, dagdir, dagout, jobstate_log, jobs))
        self.u.write_json (dagmetas, 'dagmeta.js', preamble = 'var dagmeta = ')

    def get_dagmeta (self, dag, dagdir, dagout, jobstate_log, jobs):
        jobmeta = {}
        for key in jobs:
            job = jobs [key]
            jobmeta [key] = job.get_meta ()
        return {
            'jobstate' : jobstate_log,
            'dag'      : dag,
            'dagdir'   : os.path.abspath (dagdir),
            'dagout'   : dagout,
            'runs'     : [],
            'jobs'     : jobmeta
            }

    def main (self):
        ''' Parse arguments. '''
        parser = argparse.ArgumentParser ()
        parser.add_argument ("-p", "--prep",        help="Prepare.", action='store_true', default=True)
        parser.add_argument ("-m", "--monitor",     help="Monitor.", action='store_true', default=False)
        parser.add_argument ("-w", "--write",       help="Write.",   action='store_true', default=False)
        parser.add_argument ("-l", "--loglevel",    help="Log level.", default="error")
        args = parser.parse_args ()
        
        numeric_level = getattr (logging, args.loglevel.upper (), None)
        assert isinstance (numeric_level, int), "Undefined log level: %s" % args.loglevel
        logging.basicConfig (level=numeric_level, format='%(asctime)-15s %(message)s')
        
        if args.prep:
            self.prepare ('.')
        if args.monitor:
            logger.debug ("Running monitor")
            self.monitor ()
        if args.write:
            self.write_output ()

#app = DAGDebug ()
#app.main ()


