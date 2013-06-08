function G4D () {
    this.templates = {

	'v_legend' : [ '<div id="legend">',
		       '{{#legend_items}}',
		       '  <div>',
		       '    <div class="legend">{{name}}</div>',
		       '    <img class="status_img legend_img" src="/static/img/{{imageName}}.jpg"></img>',
		       '  </div>',
		       '{{/legend_items}}',
		       '<div>' ].join (''),

	'v_flows' : [ '<table class="flowroot" cellpadding="0">',
		      '  <tr class="flowhead"><td>Workflows</td></tr>',
		      '  {{#flows}}',
		      '  <tr class="flowcontext">',
		      '    <td>',
		      '      <table class="flowgroup" cellpadding="0"> ', // flow elements.
		      '        <tr class="flow">',
		      '          <td width="40%" class="flowpath">{{name}}</td>',
		      '          <td width="5%"><img class="status_img" src="/static/img/{{exit_status}}.jpg"</img></td>',
		      '          <td width="15%" class="flow_jobs" flow="{{full_path}}"><p class="flow_hov">Jobs</p></td>',
		      '          <td width="20%"><p class="flow_hov art_dag" file="*.dag">DAG</p></td>',
		      '          <td width="20%"><p class="flow_hov art_dagmanout" file="*.dagman.out">Log</p></td>',
		      '        </tr>',
		      '        <tr>',                   // flow details.
		      '          <td class="flowdata" colspan="5"></td>',
		      '        </tr>',
		      '      </table>',
		      '    </td>',
		      '  </tr>',		      
		      '  {{/flows}}',
		      '</table>' ].join (''),

	'v_jobs'  : [ '<table class="jobs dynamicdata" cellpadding="0">',
		      '  <tr class="job_header">',
		      '    <th>Name</th>',
		      '    <th>Status</th>',
		      '    <th>Condor Submit File</th>',
		      '    <th>Executable</th>',
		      '    <th>StdErr</th>',
		      '    <th>StdOut</th>',
		      '    <th>XML</th>',
		      '  </tr>',
		      '  {{#jobs}}',
		      '  <tr flow="{{exec_job_id}}">',
		      '    <td width="15%" class="job_execjobid">{{exec_job_id}}</td>',
		      '    <td width="15%" class="job_status"><img class="status_img" src="/static/img/{{status}}.jpg"</img></td>',
/*
		      '    <td class="art_submitfile" file="{{submit_file}}">submit</td>',
		      '    <td class="art_executable" file="{{executable}}">executable</td>',
		      '    <td class="art_stderr"     file="{{exec_job_id}}.err">stderr</td>',
		      '    <td class="art_stdout"     file="{{exec_job_id}}.out">stdout</td>',
		      '    <td class="art_xml"        file="*xml">xml</td>',
*/
		      '    <td width="15%" class="art_submitfile" file="{{submit_file}}"></td>',
		      '    <td width="15%" class="art_executable" file="{{executable}}"></td>',
		      '    <td width="15%" class="art_stderr"     file="{{exec_job_id}}.err"></td>',
		      '    <td width="15%" class="art_stdout"     file="{{exec_job_id}}.out"></td>',
		      '    <td width="15%" class="art_xml"        file="*xml"></td>',
		      '  </tr>',
		      '  {{/jobs}}',
		      '  <tr>',
		      '    <td colspan="7" class="jobdata">',
		      '    </td>',
		      '  </tr>',
		      '</table>' ].join (''),

	'v_file' : '<pre class="dynamicdata"><code>{{file}}</code></pre>'

    };
};
G4D.prototype.render = function (obj, template, selector) {
    var template = this.templates [template];
    var html = Mustache.to_html (template, obj);
    $(selector).html (html);
};
G4D.prototype.controller = function (url, view, selector, register, cb) {
    gjax.getJSON (url,
		  function (obj) {
		      g4d.render (obj, view, selector);
		      if (register && register instanceof Array) {
			  if (register.length > 0) {
			      if (register[0] instanceof Array) {
				  for (var c = 0; c < register.length; c++) {
				      g4d.register (register [c]);
				  }
			      } else {
				  g4d.register (register);
			      }
			  }
		      }
		      if (cb) {
			  cb ();
		      }
		  });    
}
G4D.prototype.register = function (r) {
    var selector = r [0];
    var event = r [1];
    var action = r [2];
    $(selector).on (event, action);
};
G4D.prototype.init = function () {
    g4d.controller ('/api/workflows', 'v_flows', '#main',
		    [
			[ '.flow .flow_jobs',        'click', g4d.getJobs ],
			[ '.flow .art_dag',          'click', g4d.displayFlowData ],
			[ '.flow .art_dagmanout',    'click', g4d.displayFlowData ]
		    ],
		    function () {
			$('.flowgroup').hover (function (e) {
			    $(this).find ('.flow_hov').show ();
			},
					       function (e) {
						   $(this).find ('.flow_hov').hide ();
					       });
		    });
    g4d.render ({
	legend_items : [
	    { name : "Running",    imageName : "running" },
	    { name : "Succeeded",  imageName : "succeeded" },
	    { name : "Failed",     imageName : "failed" },
	    { name : "Held",       imageName : "held" },
	    { name : "Terminated", imageName : "terminated" },
	]
    }, 'v_legend', '#footer');
};
G4D.prototype.getJobs = function (e) {
    $('.jobdata pre').remove ();
    $('.flowdata .dynamicdata').remove ();
    var flow = $(this).attr ('flow');
    flow = flow.substring (1);
    var active = [ '.flowdata .jobs .art_submitfile',
		   '.flowdata .jobs .art_executable',
		   '.flowdata .jobs .art_stdout',
		   '.flowdata .jobs .art_stderr',
		   '.flowdata .jobs .art_xml' ];
    var service = '/api/jobs?workflow=' + flow;
    g4d.controller (service, 'v_jobs', $(this).parent().parent().find ('.flowdata'),
		    g4d.generateEventSubscriptions (active),
		    function () {
			for (var c = 0; c < active.length; c++) {
			    var selector = active [c];
			    $(selector).addClass ('active');
			}
			//d3model (x);
		    });
};
G4D.prototype.displayFlowData = function (e) {
    $('.jobdata pre').remove ();
    $('.flowdata .dynamicdata').remove ();
    g4d.getArtifact (e, '.flowgroup', '.flowdata');
};
G4D.prototype.displayJobData = function (e) {
    g4d.getArtifact (e, '.jobs', '.jobdata');
};
G4D.prototype.getArtifact = function (e, parent, display) {
    var classNames = $(e.target).attr ('class').split (' ');
    for (var c = 0; c < classNames.length; c++) {
	var className = classNames [c];
	if (className.startsWith ('art_')) {
	    var start = className.indexOf ('art_');
	    var artifact = className.substring (start + 4);
	    var flow = $(e.target).closest ('.flowgroup').find ('.flow_jobs').attr ('flow');
	    flow = dirname (flow);
	    var file = flow + '/' + $(e.target).attr ('file');
	    //var selector = $(this).closest('.jobs').find ('.jobdata');
	    var selector = $(e.target).closest(parent).find (display);
	    var service = '/api/artifact?file=' + file;
	    if (file.indexOf ('*') > -1) {
		service = service + '&pattern=True';
	    }
	    g4d.controller (service, 'v_file', selector,
			    [],
			    function () {
				var text = $(selector).html ();
				$(selector).html (text).css ({ 'display' : 'block' });
				$('pre').each(function(i, e) {
				    hljs.highlightBlock (e);
				});
			    });
	    
	    break;
	}
    }
};
G4D.prototype.getExtension = function (text) {
    var result = null;
    text = basename (text);
    var index = text.lastIndexOf ('.');
    if (index > -1) {
	result = text.substring (index + 1);
    }
    return result;
};
G4D.prototype.generateEventSubscriptions = function (selectors) {
    var subscriptions = [];
    for (var c = 0; c < selectors.length; c++) {
	var selector = selectors [c];
	subscriptions.push ( [ selector, 'click', g4d.displayJobData ]);
    }
    return subscriptions;
};

var x = {
    "name": "flow",
    "children": [
	{
	    "name": "analytics",
	    "children": [
		{
		    "name": "cluster",
		    "children": [
			{"name": "AgglomerativeCluster", "size": 3938},
			{"name": "CommunityStructure", "size": 3812},
			{"name": "HierarchicalCluster", "size": 6714},
			{"name": "MergeEdge", "size": 743}
		    ]
		},
		{
		    "name": "graph",
		    "children": [
			{"name": "BetweennessCentrality", "size": 3534},
			{"name": "LinkDistance", "size": 5731},
			{"name": "MaxFlowMinCut", "size": 7840},
			{"name": "ShortestPaths", "size": 5914},
			{"name": "SpanningTree", "size": 3416}
		    ]
		}
	    ]
	}
    ]
};

var g4d = new G4D ();

$(function () {
    g4d.init ();
    hljs.initHighlightingOnLoad ();
});
