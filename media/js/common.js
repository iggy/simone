/////////////////////////// globals, etc.

// A few handy shortcuts
var $U = YAHOO.util;
var $D = YAHOO.util.Dom;
var $ = YAHOO.util.Dom.get;
// setup a namespace for django-webmail
YAHOO.namespace('dw');


// make update manager parse any scripts it gets back from the server
YAHOO.util.Event.on(window, 'load', function() {
        Ext.UpdateManager.defaults.loadScripts=true;
    }
);

//////////////////////////// some functions used on the main page
function updateMsgList(url) {
	Ext.get('msglistwrap').load(url);
}
function showSpinner() {
    var showspinner = new YAHOO.util.Anim('spinner', {
            //height: { to: 40 },
            opacity: { to: 100 },
        }, 0.5, YAHOO.util.Easing.easeOut);
    showspinner.animate();
}
function hideSpinner() {
    var hidespinner = new YAHOO.util.Anim('spinner', {
            //height: { to: 0 },
            opacity: {to: 0 },
        }, 0.5, YAHOO.util.Easing.easeOut);
    hidespinner.animate();
}
YAHOO.util.Event.on(window, 'load', hideSpinner);

function initLinks() {
    // setup  the new mail link
    Ext.get('newmaillink').on('click', function(el,e) {
        Ext.get('contentpane').load('newmail/');
        YAHOO.util.Event.stopEvent(e);
    });
    Ext.get('prefslink').on('click', function(el, e) {
        Ext.get('contentpane').load('config/view/');
        YAHOO.util.Event.stopEvent(e);
    });
}
YAHOO.util.Event.addListener(window, 'load', initLinks, true);


//////////////////////////// some config page functions
function initSrvLinks() {
    function srvEditLinkOnClick(ev, el) {
        // get the id of the server we want to replace
        var sid = el.id.replace('_edit_link');

        // show the editor in a new tr below the current line
    }
	function srvRemLinkOnClick(ev, el) {
		// verify they really want to do this
		// get the id of the server we are removing

		// call back to handle the remove server ajax request
		function RSCSuccess(o) {
				// we get back a json response
				// hide the tr that had the srv we just removed
		}

		// send an ajax request to remove the server
	}


    eln = YAHOO.util.Dom.getElementsByClassName('srv_edit_link');
    rln = YAHOO.util.Dom.getElementsByClassName('srv_rm_link');
    YAHOO.util.Event.addListener(eln, srvEditLinkOnClick);
	YAHOO.util.Event.addListener(rln, srvRemLinkOnClick);
}


//////////////////////////// some general use functions

// zebra stripe a table
// requires css classes even and odd
function stripe(id) {

	// the flag we will use to keep track of 
	// whether the current row is odd or even
	var even = false;

	// obtain a reference to the desired table
	// if no such table exists, abort
	var table = document.getElementById(id);
	if (! table) { alert("no table selected"); return; }
	
	// by definition, tables can have more than one tbody
	// element, so we will have to get the list of child
	// tbodys 
	var tbodies = table.getElementsByTagName("tbody");

	// and iterate through them...
	for (var h = 0; h < tbodies.length; h++) {	
		// find all the tr elements... 
		var trs = tbodies[h].getElementsByTagName("tr");
		// ... and iterate through them
		for (var i = 0; i < trs.length; i++) {
				trs[i].className=even ? "even" : "odd";
				// flip from odd to even, or vice-versa
				even =  ! even;
		}
	}
}


function sendMail(formel) {
	var callback = {
		success:	function(o) {
			console.log(o);
			$U.Dom.get('contentpane').innerHTML = o.responseText;
		},
		failure:	function(o) {
			console.log(o);
		}
	}

	$U.Connect.setForm(formel);

	$U.Connect.asyncRequest('GET', formel.action, callback);

	// don't want the form to actually submit
	return false;
}

/*
 * load an element with content from source
 * what = element to fill
 * source = url|var to put into 
 */
YAHOO.dw.load = function(what, source) {
	if(source[0] == '/') { // FIXME need to do MUCH more exhaustive checking
		// source is a url I think
		console.log('url', what, source);
		var callback = {
			success: function(o) {
				what = o.argument[0];
				$U.Dom.get(what).innerHTML = o.responseText;
			},
			failure: function(o) {
				;
			},
			argument: [what]
		}
		$U.Connect.asyncRequest('GET', source, callback);
	} else {
		// source is a var
		console.log('var', what, source);
		$U.Dom.get(what).innerHTML = source;
	}
}
YAHOO.dw.load('contentpane', 'some text');