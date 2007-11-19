/////////////////////////// globals, etc.

// A few handy shortcuts
var $U = YAHOO.util;
var $D = YAHOO.util.Dom;
var $ = YAHOO.util.Dom.get;
// setup a namespace for django-webmail
YAHOO.namespace('dw');

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
		//YAHOO.dw.load('contentpane', 'newmail/');
		YAHOO.dw.newmail.newpanel = new YAHOO.widget.Panel('newmsgpanel', {
			width:'800px',
			height:'600px',
			fixedcenter: true,
			draggable:false,
			constraintoviewport: true,
			close:true,
			visible:true
		});
		YAHOO.dw.newmail.newpanel.setHeader('Compose');
		YAHOO.dw.newmail.newpanel.setBody('<div id="newmsgdiv"></div>');
		YAHOO.dw.newmail.newpanel.setFooter('&nbsp;');
		YAHOO.dw.newmail.newpanel.render(document.body);
		YAHOO.dw.newmail.newpanel.show();
		YAHOO.dw.load('newmsgdiv', 'newmail/');

		// if they like the rich editor as their default, make it so
		if(YAHOO.dw.config.defaultEditor == '2')
			YAHOO.dw.newmail.initRTE();

		if(e)
			YAHOO.util.Event.stopEvent(e);
	});
	$U.Event.on('prefslink', 'click', function(el, e) {
		//Ext.get('contentpane').load('config/view/');
		// hide the msglist datatable
		$D.addClass('msglist', 'hidden');
		$D.removeClass('contentpane', 'hidden');
		YAHOO.dw.load('contentpane', 'config/view/');
		if(e)
			$U.Event.stopEvent(e);
	});
}
YAHOO.util.Event.addListener(window, 'load', initLinks, true);

YAHOO.namespace('dw.newmail');
YAHOO.dw.newmail.usingRTE = false;
YAHOO.dw.newmail.initRTE = function() {
	//The Editor config
	var myConfig = {
		height: '300px',
		width: '730px',
		animate: true,
		dompath: true,
		focusAtStart: true,
		handleSubmit: true
	};

	//Now let's load the Editor..
	YAHOO.dw.newmail.Editor = new YAHOO.widget.Editor('editor', myConfig);
	YAHOO.dw.newmail.Editor.render();

	// set a flag that says we are using the RTE so we can check it in the actual send msg function
	$('usingRTE').value = true;
	YAHOO.dw.newmail.usingRTE = true;
}

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



YAHOO.dw.editServer = function(srvtype, formel, saction) {
	var callback = {
		success: function(o) {
			resp = eval('('+o.responseText+')');
			console.log('editServer callback', o, resp);
			if(resp.status == "OK") {
				// tell them it was successful
				// refresh the folder lists
				$D.get('foldertree').innerHTML = '';
				YAHOO.dw.showServers();
				// refresh the config panel
				YAHOO.dw.load('contentpane', 'config/view/');
				console.log(resp);
			} else {
				// tell them editing the server failed and hopefully why
				console.log(resp);
			}
		},
		failure: function(o) {
		}
	}
	formel = $D.get(formel);
	$U.Connect.setForm(formel);
	$U.Connect.asyncRequest('GET', 'config/edit/?saction='+saction+'&srvtype='+srvtype, callback);
	//YAHOO.util.Event.stopEvent();
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
			resp = eval('('+o.responseText+')');
			if(resp.status == 'ERROR') {
				$U.Dom.addClass('sendMailMsg', 'alert');
				$U.Dom.get('sendMailMsg').innerHTML = resp.message;
			} else if(resp.status == 'SUCCESS') {
				$U.Dom.addClass('newmailEditorWrapper', 'hidden');
				window.setTimeout(3000, function() {
					YAHOO.dw.msglist.newpanel.destroy();
				});
			}
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
//YAHOO.dw.load('contentpane', 'some text');


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
//YAHOO.util.Event.addListener(window, 'load', YAHOO.dw.showServers);


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
				$D.addClass('contentpane', 'hidden');
				$D.removeClass('msglist', 'hidden');
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

// initialize the msg list... gets called when users login or when they click on a folder name in the tree of folders
YAHOO.dw.msglist.init = function(e, o) {
	var subjectFormatter = function(elCell, oRecord, oColumn, oData) {
		YAHOO.dw.msglist.msgseen = false;
		record = oRecord.getData();
		console.log('subjectFormatter: ', elCell, oRecord, oColumn, oData, YAHOO.dw.msglist.msgseen);
		for(var i = 0 ; i < record.flags.length ; i++) {
			console.log(record.flags[i], record,record.flags[i].indexOf('\Seen') );
			if(record.flags[i].indexOf('\Seen') != -1)
				YAHOO.dw.msglist.msgseen = true;
		}
		console.log(YAHOO.dw.msglist.msgseen);
		if(YAHOO.dw.msglist.msgseen == false)
			$D.addClass(elCell.parentNode, 'unread-msg');
		else
			$D.removeClass(elCell.parentNode, 'unread-msg');
		elCell.innerHTML = oData;
	}
	var flagsFormatter = function(elCell, oRecord, oColumn, oData) {
		YAHOO.dw.msglist.msgreplied = false;
		YAHOO.dw.msglist.msgflagged = false;

		record = oRecord.getData();
		console.log('flagsFormatter: ', elCell, oRecord, oColumn, oData);
		for(var i = 0 ; i < record.flags.length ; i++) {
			console.log(record.flags[i], record);
			if(record.flags[i].indexOf('\Answered') != -1)
				YAHOO.dw.msglist.msgreplied = true;
			if(record.flags[i].indexOf('\Flagged') != -1)
				YAHOO.dw.msglist.msgflagged = true;
		}
		var html = '';
		if(YAHOO.dw.msglist.msgreplied == true)
			html += 'R';
		if(YAHOO.dw.msglist.msgflagged == true)
			html += 'F';

		elCell.innerHTML = html;
	}

	server = o.server;
	folder = o.folder;
	console.log(e, o);
	YAHOO.dw.msglist.ds = new $U.DataSource('json/msglist/');
	YAHOO.dw.msglist.ds.responseType = $U.DataSource.TYPE_JSON;
	YAHOO.dw.msglist.ds.responseSchema = {
		resultsList: 'msgs',
		fields: ['uid', 'size','fromtext','fromemail','flags','date','subject','folder','server']
	};
	YAHOO.dw.msglist.coldefs = [
		{key:'flags', label:'Flags', formatter:flagsFormatter},
		{key:'subject', label:'Subject', /*sortable:true,*/ formatter:subjectFormatter},
		{key:'fromtext', label:'From', /*sortable:true*/},
		{key:'date', label:'Date', /*sortable:true,*/ formatter:"date"},
		{key:'size', label:'Size', /*sortable:true*/}

	];
	YAHOO.dw.msglist.opts = {
		//paginated:true,
		//paginator: {containers:null,dropdownOptions:[20,50,100],rowsPerPage:20,pageLinks: 5},
		//sortedBy: {key:'date', dir:'asc'},
		initialRequest: '?server='+server+'&folder='+folder+'&start=1&end=20'
	}
	YAHOO.dw.msglist.dt = new YAHOO.widget.DataTable('msglist', YAHOO.dw.msglist.coldefs,YAHOO.dw.msglist.ds, YAHOO.dw.msglist.opts);

	// Custom code to parse the raw server data for Paginator values and page links
	YAHOO.dw.msglist.ds.doBeforeCallback = function(oRequest, oRawResponse, oParsedResponse) {
		// clear the Bold
		//var oSelf = YAHOO.example.ServerPagination;
		//var oDataTable = oSelf.myDataTable;

		// Get Paginator values
		var oRawResponse = eval('('+oRawResponse+')'); //JSON.parse(oRawResponse); // Parse the JSON data
		var recordsReturned = oRawResponse.records; // How many records this page
		var startIndex = oRawResponse.start; // Start record index this page
		var endIndex = oRawResponse.end; // End record index this page
		var totalRecords = oRawResponse.count; // Total records all pages

		// Update the DataTable Paginator with new values
		var newPag = {
			rowsPerPage: recordsReturned,
			recordsReturned: recordsReturned,
			startRecordIndex: parseFloat(startIndex),
			endIndex: endIndex,
			totalResults: totalRecords,
			totalRecords: totalRecords
		}
		YAHOO.dw.msglist.dt.updatePaginator(newPag);

		// Update the links UI
		YAHOO.util.Dom.get("prevLink").innerHTML = (startIndex == 1) ? "<" :
				"<a href=\"#previous\" alt=\"Show previous items\"><</a>" ;
		YAHOO.util.Dom.get("nextLink").innerHTML =
				(endIndex >= totalRecords) ? ">" :
				"<a href=\"#next\" alt=\"Show next items\">></a>";
		YAHOO.util.Dom.get("startIndex").innerHTML = startIndex;
		YAHOO.util.Dom.get("endIndex").innerHTML = endIndex;
		YAHOO.util.Dom.get("ofTotal").innerHTML = " of " + totalRecords;

		// Let the DataSource parse the rest of the response
		return oParsedResponse;
	};
	// Hook up custom pagination
	YAHOO.dw.msglist.getPage = function(start, end) {
		// If a new value is not passed in
		// use the old value
		if(!YAHOO.lang.isValue(end)) {
			nResults = YAHOO.dw.msglist.dt.get("paginator").count;
		}
		// Invalid value
		if(!YAHOO.lang.isValue(start)) {
			return;
		}
		console.log('getPage: ', start, end);
		var newRequest = '?server='+server+'&folder='+folder+'&start=' + start + '&end=' + end;
		YAHOO.dw.msglist.ds.sendRequest(newRequest, YAHOO.dw.msglist.dt.onDataReturnInitializeTable, YAHOO.dw.msglist.dt);
	};
	YAHOO.dw.msglist.getPreviousPage = function(e) {
		YAHOO.util.Event.stopEvent(e);
		// Already at first page
		var p = YAHOO.dw.msglist.dt.get("paginator");
		console.log('getPrevPage: ', p);
		if(p.startRecordIndex == 1) {
			return;
		}
		var newStartRecordIndex = p.startRecordIndex - 20;
		YAHOO.dw.msglist.getPage(newStartRecordIndex, newStartRecordIndex + p.rowsThisPage);
	};
	YAHOO.dw.msglist.getNextPage = function(e) {
		YAHOO.util.Event.stopEvent(e);
		// Already at last page
		var p = YAHOO.dw.msglist.dt.get("paginator");
		console.log('getNextPage: ', p);
		if(p.startRecordIndex + p.rowsThisPage >= p.totalRecords) {
			//return;
		}
		//var newStartRecordIndex = (parseFloat(p.startRecordIndex) + parseFloat(p.rowsThisPage));
		var newStartRecordIndex = (p.startRecordIndex + 20);
		YAHOO.dw.msglist.getPage(newStartRecordIndex, newStartRecordIndex+p.rowsThisPage);
	};
	YAHOO.util.Event.addListener(YAHOO.util.Dom.get("prevLink"), "click", YAHOO.dw.msglist.getPreviousPage, this, true);
	YAHOO.util.Event.addListener(YAHOO.util.Dom.get("nextLink"), "click", YAHOO.dw.msglist.getNextPage, this, true);

	YAHOO.dw.msglist.dt.subscribe('cellClickEvent', YAHOO.dw.msglist.cellClick);
}
//YAHOO.util.Event.addListener(window, 'load', YAHOO.dw.msglist.init, {server:0, folder:'INBOX'});

// the function that gets called when you click on an email in the message list
YAHOO.dw.msglist.cellClick = function(o) {
	var record = YAHOO.dw.msglist.dt.getRecord(o.target).getData();
	console.log(o, record);
	YAHOO.dw.msglist.viewpanel = new YAHOO.widget.Panel('msgpanel', {
		width:'800px',
		height:'600px',
		fixedcenter: true,
		constraintoviewport: true,
		close:true,
		visible:true
	});
	YAHOO.dw.msglist.viewpanel.setHeader('View Mail');
	YAHOO.dw.msglist.viewpanel.setBody('<div id="viewmsgdiv"></div>');
	YAHOO.dw.msglist.viewpanel.setFooter('&nbsp;');
	YAHOO.dw.msglist.viewpanel.render(document.body);
	YAHOO.dw.msglist.viewpanel.show();
	YAHOO.dw.load('viewmsgdiv', 'viewmsg/'+record.server+'/'+record.folder+'/'+record.uid+'/');
}

YAHOO.dw.newServer = function(srvtype) {
	YAHOO.dw.newSRVpanel = new YAHOO.widget.Panel('panel', {
		width:'800px',
		height:'600px',
		fixedcenter: true,
		constraintoviewport: true,
		close:true,
		visible:true
	});
	YAHOO.dw.newSRVpanel.setHeader('Enter New '+srvtype+' Server Settings');
	YAHOO.dw.newSRVpanel.setBody('<div id="newserver"></div>');
	YAHOO.dw.newSRVpanel.setFooter('&nbsp;');
	YAHOO.dw.newSRVpanel.render(document.body);
	YAHOO.dw.newSRVpanel.show();
	YAHOO.dw.load('newserver', 'config/new'+srvtype+'form/');
}

YAHOO.dw.submitNewServer = function(formel) {
	var callback = {
		success: function(o) {
			alert(o);
		},
		failure: function(o) {
		}
	}
	$U.Connect.setForm(formel);
	$U.Connect.asyncRequest('GET', 'config/addnew/', callback);
}

