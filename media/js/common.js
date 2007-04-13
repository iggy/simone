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