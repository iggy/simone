/////////////////////////// globals, etc.
// make update manager parse any scripts it gets back from the server
YAHOO.util.Event.on(window, 'load', function() {
        Ext.UpdateManager.defaults.loadScripts=true;
    }
);

//////////////////////////// some functions used on the main page
function updateMsgList(url) {
	_$('msglistwrap').populate(url);
}
function showSpinner() {
    var showspinner = new YAHOO.util.Anim('spinner', {
            //height: { to: 40 },
            opacity: { to: 100 },
        }, 0.25, YAHOO.util.Easing.easeOut);
    showspinner.animate();
}
function hideSpinner() {
    var hidespinner = new YAHOO.util.Anim('spinner', {
            //height: { to: 0 },
            opacity: {to: 0 },
        }, 0.25, YAHOO.util.Easing.easeOut);
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

    eln = YAHOO.util.Dom.getElementsByClassName('srv_edit_link');
    rln = YAHOO.util.Dom.getElementsByClassName('srv_rm_link');
    YAHOO.util.Event.addListener(eln, srvEditLinkOnClick);
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
	function callback(el, suc, resp) {
		if(suc == false)
			Ext.get('contentpane').update(resp.responseText); // FIXME this can be dropped in the future
	}
	Ext.get('contentpane').load(formel.action, 
		{
			newmailfrom:formel.newmailfrom.value,
			newmailto:formel.newmailto.value,
			newmailsubject:formel.newmailsubject.value,
			editor:formel.editor.value,
		},
		callback
	);
	// don't want the form to actually submit
	return false;
}