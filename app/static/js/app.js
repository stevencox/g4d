/**
 * The Grayson for DAGMan app.
 */
function G4D () {
};
/**
 * Render data to a template and insert the results into a document element
 * designated by the specified selector.
 */
G4D.prototype.render = function (obj, template, selector) {
    var template = this.templates [template];
    var html = Mustache.to_html (template, obj);
    $(selector).html (html);
};
/**
 * Invoke a service.
 *   Render the results via the given view into the document selector.
 *   Perform event registrations based on the register parameter.
 *   Invoke the given callback if supplied.
 */
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
/**
 * Register for events given an array of selector, event, action tuples.
 */
G4D.prototype.register = function (r) {
    var selector = r [0];
    var event = r [1];
    var action = r [2];
    $(selector).on (event, action);
};
/**
 * Cofigure the application.
 * Load templates into the document.
 * Initialize the page once templates are loaded.
 */
G4D.prototype.configure = function () {
    hljs.initHighlightingOnLoad ();
    gjax.get ('/static/templates/views.html',
	      function (text) {
		  g4d.templates = {};
		  $('body').append (text);
		  $('.views .template').each (function (i) {
		      var id = $(this).attr ('id');
		      var text = $(this).val ();
		      console.log (text);
		      g4d.templates [id] = text;
		  });
		  g4d.init ();
	      });
};    
/**
 * 
 */
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
	    { name : "Submitted",  imageName : "submitted" },
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
    var active = [ '.flowdata .jobs p' ];
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
// firefox and colspan.
// http://www.dynamicdrive.com/forums/showthread.php?55999-Toggle-table-row-FireFox-ignoring-colspan
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
	    var selector = $(e.target).closest(parent).find (display);
	    var service = '/api/artifact?file=' + file;
	    if (file.indexOf ('*') > -1) {
		service = service + '&pattern=True';
	    }
	    g4d.controller (service, 'v_file', selector,
			    [],
			    function () {
				var text = $(selector).html ();

				$(selector).html (text).css ({ 'display' : '' });
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
    g4d.configure ();
});
