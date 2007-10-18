/////////////////////////// globals, etc.

// A few handy shortcuts
var $U = YAHOO.util;
var $D = YAHOO.util.Dom;
var $ = YAHOO.util.Dom.get;
// setup a namespace for django-webmail
YAHOO.namespace('dw');


// make update manager parse any scripts it gets back from the server
//YAHOO.util.Event.on(window, 'load', function() {
//        Ext.UpdateManager.defaults.loadScripts=true;
//    }
//);

//////////////////////////// some functions used on the main page
function updateMsgList(url) {
	//Ext.get('msglistwrap').load(url);
	YAHOO.dw.load('msglistwrap', url);
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
    $U.Event.on('newmaillink', 'click', function(el,e) {
        //Ext.get('contentpane').load('newmail/');
	YAHOO.dw.load('contentpane', 'newmail/');
        if(e)
		YAHOO.util.Event.stopEvent(e);
    });
    $U.Event.on('prefslink', 'click', function(el, e) {
        //Ext.get('contentpane').load('config/view/');
	YAHOO.dw.load('contentpane', 'config/view/');
        if(e)
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

	$U.Connect.asyncRequest('POST', formel.action, callback);

	// don't want the form to actually submit
	return false;
}

/*
 * load an element with content from source
 * what = element to fill
 * source = url|var to put into 
 */
// FIXME if we think the source is a url and try to load it and it fails, maybe 
// it wasn't really a url and we need to load it like it was a string
YAHOO.dw.load = function(what, source) {
	if(!$(what))
		return false;
	if(source[0] == '/' || source[source.length-1] == '/') { // FIXME need to do MUCH more exhaustive checking
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
		$(what).innerHTML = source;
	}
}
YAHOO.dw.load('contentpane', 'some text');


YAHOO.dw.showServers = function(server) {
	var callback = {
		success: function(o) {
			resp = eval('('+o.responseText+')');
			console.log(resp, resp.servers.length);
			for(var i = 0 ; i < resp.servers.length ; i++) {
				console.log('showing folders for server: '+i);
				YAHOO.dw.showFolders(resp.servers[i]);
			}
		},
		failure: function(o) {
			console.log(o);
		}
	}
	$U.Connect.asyncRequest('GET', 'json/serverlist/', callback);
}
YAHOO.util.Event.addListener(window, 'load', YAHOO.dw.showServers);


YAHOO.dw.showFolders = function(serverObj) {
	var callback = {
		success: function(o) {
			serverObj = o.argument[0];
		
			function onLabelClick(node) {
				// we need to rebuild the folder name from the (sub)dir names
				realfoldername = node.label;
				while(node.parent.depth != -1) {
					realfoldername = node.parent.label+'.'+realfoldername;
					node = node.parent;
				}
		
				//YAHOO.dw.load('contentpane', 'msglist/'+realfoldername+'/');
				YAHOO.dw.msglist.init({}, {server:0, folder:realfoldername});
			}
		
			resp = eval('('+o.responseText+')');
			console.log('showFolders success callback', o, resp);
			
			// put a label with the server name/address at the top of the tree
			var label = document.createElement('h3');
			label.innerHTML = serverObj[1];
			$D.get('foldertree').appendChild(label);
			
			// make a new div in the foldertree container div to attach this to
			var el = document.createElement('div');
			$D.get('foldertree').appendChild(el);
			
			var tree = new YAHOO.widget.TreeView(el);
			var tvNodes = [];
			var root = tree.getRoot();
			//var tmpNode = new YAHOO.widget.TextNode("mylabel", root, false); 
			for(var i = 0 ; i < resp.length ; i++) {
				f = resp[i].split('.');
				//console.log(resp[i], f);
				for(var j=0 ; j < f.length ; j++) {
					//console.log(f[j]);
					// f[i] should equal an actual (sub)dir name (i.e. the part between .'s)
					if(j == 0)
						root = tree.getRoot();
					else
						root = tvNodes[f[j-1]];
					nodename = f[j].replace(' ', '_'); // clean spaces out
					if(!tvNodes[nodename]) {
						tvNodes[nodename] = new YAHOO.widget.TextNode(f[j], root, false);
						tvNodes[nodename].onLabelClick = onLabelClick;
					}
				}

			}
			tree.draw();
			console.log('tree drawn');
		},
		failure: function(o) {
			;
		},
		argument: [serverObj]
	}
	$U.Connect.asyncRequest('GET', 'json/folderlist/?server='+serverObj[0], callback);

}

YAHOO.namespace('dw.msglist');
YAHOO.dw.msglist.init = function(e, o) {
	server = o.server;
	folder = o.folder;
	console.log(e, o);
	YAHOO.dw.msglist.ds = new $U.DataSource('json/msglist/?server='+server+'&folder='+folder);
	YAHOO.dw.msglist.ds.responseType = $U.DataSource.TYPE_JSON;
	YAHOO.dw.msglist.ds.responseSchema = {
		resultsList: 'msgs',
		fields: ['uid', 'size','fromtext','fromemail','flags','date','subject','folder']
	};
	YAHOO.dw.msglist.coldefs = [
		{key:'subject', label:'Subject', sortable:true},
		{key:'fromtext', label:'From', sortable:true},
		{key:'date', label:'Date', sortable:true, formatter:"date"},
		{key:'size', label:'Size', sortable:true}
	];
	YAHOO.dw.msglist.opts = {
		sortedBy: {key:'date', dir:'asc'},
		initialRequest: ""
	}
	YAHOO.dw.msglist.dt = new YAHOO.widget.DataTable('contentpane', YAHOO.dw.msglist.coldefs,YAHOO.dw.msglist.ds, YAHOO.dw.msglist.opts);
	
	YAHOO.dw.msglist.dt.subscribe('cellClickEvent', YAHOO.dw.msglist.cellClick);
}
YAHOO.util.Event.addListener(window, 'load', YAHOO.dw.msglist.init, {server:0, folder:'INBOX'});

YAHOO.dw.msglist.cellClick = function(o) {
	var record = YAHOO.dw.msglist.dt.getRecord(o.target).getData();
	console.log(o, record);
	YAHOO.dw.load('contentpane', 'viewmsg/'+record.folder+'/'+record.uid+'/');
}


