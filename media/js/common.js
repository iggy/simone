function updateMsgList(url) {
	_$('msglistwrap').populate(url);
}


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

function addScriptEl(script) {
	var head = document.getElementsByTagName('head')[0];
	var s = document.createElement('script');
	s.src = script;
	s.type = 'text/javascript';
	head.appendChild(s);
}

function evalScripts(html) {
	var s = document.getElementsByTagName("script");
	var docHead = document.getElementsByTagName("head")[0];

//	For browsers which discard scripts when inserting innerHTML,
//	extract the scripts using a RegExp
	if (s.length == 0)
	{
		var re = /(?:<script.*(?:src=[\"\'](.*)[\"\']).*>.*<\/script>)|(?:<script.*>([\S\s]*?)<\/script>)/ig; // assumes HTML well formed and then loop through it.
		var match;
		while (match = re.exec(html))
		{
			var s0 = document.createElement("script");
			if (match[1])
				s0.src = match[1];
			else if (match[2])
				s0.text = match[2];
			else
				continue;
			docHead.appendChild(s0);
		}
	}
	else
	{
		for (var i = 0; i < s.length; i++)
		{
			var s0 = document.createElement("script");
			s0.type = s[i].type;
			if (s[i].text)
			{
				s0.text = s[i].text;
			}
			else
				s0.src = s[i].src;
			docHead.appendChild(s0);
		}
	}
};

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