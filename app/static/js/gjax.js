var gjaxConf = { uriPrefix : '/' };

gjax = new Gjax ();

function Gjax () {    
};

Gjax.prototype.localizeURI = function (uri) {
    var result = uri;
    var prefix = gjaxConf.uriPrefix;
    if ( ! uri.startsWith ('/') ) {
	result = prefix == '/' ? 
	    prefix + uri : 
	    prefix + '/' + uri;
    }
    return result;
};
Gjax.prototype.getJSON = function (url, success, error) {
    this.ajax (url,	       
	      function (text) {
		  if (text) {
		      var response = gjax.parseJSON (text);
		      if (response) {
			  success (response);
		      }
		  }
	      },
	      error);

};
Gjax.prototype.getXML = function (url, success, error) {
    this.ajax (url, success, error, 'xml');
};
Gjax.prototype.postJSON = function (url, data, success, error) {
    this.post (url,
	       data,
	       function (text) {
		   if (text) {
		       var response = gjax.parseJSON (text);
		       if (response) {
			   success (response);
		       }
		   }
	       },
	       error);
};
Gjax.prototype.parseJSON = function (text) {
    var object = null;
    if (text) {
	try {
	    object = $.parseJSON (text);
	} catch (e) {
	    console.log ("JSON parse error: " + text + "\n--(error): " + e.message);
	}
    }
    return object;
};
Gjax.prototype.post = function (url, data, success, error, mimeType, method) {
    this.ajax (url, success, error, mimeType, "POST", data);
};
Gjax.prototype.get = function (url, success, error, mimeType, method) {
    this.ajax (url, success, error, mimeType);
};
Gjax.prototype.ajax = function (url, success, error, mimeType, method, data) {
    //this.progressPlus ();
    var api = this;

    if (typeof (mimeType) !== 'string') {
	mimeType = "text";
    }
    if (typeof (method) !== 'string') {
	method = "GET";
    }
    var args = {
	    type     : method,
	    url      : this.localizeURI (url), 
	    dataType : mimeType,
	    success: function (text) {
		success (text);
	    },
	    error: function (jqXHR, textStatus, errorThrown) {
		if (error) {
		    error (textStatus, errorThrown);
		} else {
		    console.log ("error: " + textStatus + " error: " + errorThrown);
		}
	    },
	    complete : function (jqXHR, textStatus) {
		//api.progressMinus ();
	    }
    };

    if (typeof (data) === 'object') {
	args ['data'] = data;
	if (!safeMethod (method) && sameOrigin (url)) {
	    data ['csrfmiddlewaretoken'] = getCookie ('csrftoken');
	}
    }
    this.ajaxStub (args);
};
Gjax.prototype.ajaxStub = function (args) {
    $.ajax (args);
};