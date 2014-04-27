/*
 * Copyright 2007-2014 Brian Jackson (iggy@theiggy.com)
 *
 * Anything not explicitly licensed some other way is released under the new BSD license
 * http://www.opensource.org/licenses/bsd-license.php
 */

// "namespaces"
var folders = {};
var msglist = {};
var dw = {}; // miscellaneous variables
dw.viewmsg = {};
dw.dialog = {};

$(document).ready(function() {
    console.log('doc ready');
    
    // refresh msg list periodically
    // TODO stuff a configurable time into the body or something
    refid = window.setInterval(function(){
        console.log('msglist refresh');
        $('#msglist .foldersel').change();
    }, 5*60*1000);

    dw.msgtable = $('#msglist').srvDatatable();

    // folder tree
    $.getJSON('json/folderlist2/?server=0&parent=', function(data) {
        console.log('fl2', data);
        $('#foldertree2').jsonTree(data, {
            mandatorySelect: true,
            lazyLoad: true,
            lazyRequestUrl: 'json/folderlist2/?server=0',
            lazySendParameterName: 'parent',
            onSelect: function(selid, selli, clickedli) {
                console.log("ft2 onSelect", selid, selli, clickedli);
                console.log(selli.attr('value'));
                $('.foldersel').val(selli.attr('value'));
                $('#msglist .foldersel').change();
            },
        });
    });
    
    // hide the spinner
    $('#spinner').hide();
});

/*
 * jQuery server side datatable plugin 0.1
 *
 * Copyright (c) 2009 Brian Jackson <iggy@theiggy.com>
 *
 * A datatable plugin that does all the searching, sorting, pagination, etc. on
 * the server. This was written mainly for Django-Webmail, which uses an IMAP
 * backend. The IMAP server will almost always be better at sorting, searching,
 * etc. It could eventually be generalized to be useful to others.
 *
 * Licensed under same license as django-webmail (i.e. BSD)
 */
;(function($) {
    $.fn.srvDatatable = function() {
        console.log('start srvDatatable', this);
        var $cnt = $(this);

        var navht = ' \
<form class="msgnav" action="msglist/" method="get" onSubmit="return false;"> \
    <input type="text" readonly="readonly" value="INBOX" class="foldersel" /> \
    <button \
        class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" \
        onclick="$(\'#msglist .pagesel\').firstPage();"> \
            <span class="ui-icon ui-icon-arrowthickstop-1-w"></span> \
    </button> \
    <button \
        class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" \
        onclick="$(\'#msglist .pagesel\').prevPage(); return false;"> \
            <span class="ui-icon ui-icon-arrowthick-1-w"></span> \
    </button> \
    <select class="pagesel ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only"> \
        <option>1</option> \
    </select> \
    <button \
        class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" \
        onclick="$(\'#msglist .pagesel\').nextPage(); return false;"> \
            <span class="ui-icon ui-icon-arrowthick-1-e"></span> \
    </button> \
    <button \
        class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" \
        onclick="$(\'#msglist .pagesel\').lastPage(); return false;"> \
            <span class="ui-icon ui-icon-arrowthickstop-1-e"></span> \
    </button> \
    Msgs Per Page: \
    <select class="perpagesel ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only"> \
        <option selected="selected">10</option> \
        <option>20</option> \
        <option>40</option> \
        <option>50</option> \
    </select> \
    Sort: \
    <select class="sortordersel ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only"> \
        <option>Asc</option> \
        <option selected="selected">Desc</option> \
    </select> \
</form> \
            ';
// TODO filters (unread, marked, etc)
        var tableht = '<table><tr> \
            <th><input type="checkbox" /></th> \
            <th style="width:60%">Subject</th> \
            <th style="width:20%">From</th> \
            <th style="width:14%">Date</th> \
            <th style="width:5%">Size</th>\
            </tr></table>';

        $cnt.append(navht);

        $cnt.append(tableht);

        $('#msglist th').addClass('ui-corner-all');

        var $foldersel = $cnt.find('.foldersel'),
            $pagesel = $cnt.find('.pagesel'),
            $perpagesel = $cnt.find('.perpagesel'),
            $sortordersel = $cnt.find('.sortordersel'),
            $tbl = $cnt.find('table');

        $foldersel.change(update);
        $pagesel.change(update);
        $perpagesel.change(update);
        $sortordersel.change(update);

        update();

        function getUrl() {
            return $cnt.find('.msgnav').attr('action') + // form action specifies the base of the url
            '0/' + // server
            $foldersel.val() + '/' + // folder
            $pagesel.val() + '/' + // page
            $perpagesel.val() + '/' + // msgs per page
            'date/'+
            $sortordersel.val().charAt(0) + '/' + // sort order
            '/'; // search terms
        };
        
        function firstPage() {
            console.log("first page", this);
            $pagesel.val('1');
            update();
            return false;
        };
        function prevPage() {
            console.log("prev page", this);
            $pagesel.val($pagesel.val()-1);
            update();
            return false;
        };
        function nextPage() {
            console.log("next page", this);
            $pagesel.val($pagesel.val()+1);
            update();
            return false;
        };
        function lastPage() {
            console.log("last page", this);
            $pagesel.val('1');
            update();
            return false;
        };
        function update() {
            $.getJSON(getUrl(), function(data) {
                console.log('get msglist callback');
                j = eval(data);
                console.log('j = ', j);

                // fill pagesel
                $pagesel.empty();
                console.log(j['totalmsgs'], $perpagesel.val(), 
                    Math.ceil(j['totalmsgs'] / $perpagesel.val()));
                for(var i = 1 ; i <= Math.max(Math.ceil(j['totalmsgs'] / $perpagesel.val()), 1) ; i++) {
                    var selht = '';
                    if($sortordersel.val().charAt(0) == "A" && i == Math.ceil(j['stop']/$perpagesel.val()))
                        selht = ' selected="selected"';
                    if($sortordersel.val().charAt(0) == "D" && i == Math.floor(j['totalmsgs']/$perpagesel.val() - j['stop']/$perpagesel.val()) + 1)
                        selht = ' selected="selected"';
                    $pagesel.append('<option'+selht+'>' + i + '</option>');
                }

                // fill the msglist table
                $tbl.find('tr:not(:first)').remove();
                console.log(j['msglist'].length);
                for(var uid in j['msglist']) {
                    msg = j['msglist'][uid];
                    console.log('168', uid, msg);
                    var rclass = 'odd';
                    if(uid % 2 == 0)
                        rclass = 'even';
                    // handle flags
                    fclass = '';
                    //console.log(msg['flags'].join());
                    if(msg['flags'].join().search("\\Seen") != -1)
                        rclass += ' msgseen';
                    else
                        rclass += ' msgunseen';
                    if(msg['flags'].join().search("\\Flagged") != -1)
                        fclass += ' msgimport';

                    // TODO finish pulling out the <*> and stuffing it into the alt tag maybe
                    r = new RegExp("&lt;.*&gt;");
                    console.log("regex5", r.exec(msg['from']));

                    $tbl.append(' \
<tr class="msg ' + rclass + '" id="msg-' + msg['uid'] + '"> \
    <td><input type="checkbox" /></td> \
    <td class="subject' + fclass + '">' + msg['subject'] + '</td> \
    <td>' + msg['from'] + '</td> \
    <td>' + msg['date'] + '</td> \
    <td>' + Math.round((msg['size']/1024)*10)/10 + 'K</td> \
</tr> \
                    ');
                }

                // msg listener
                $('tr.msg').click(function(e) {
                    console.log(this, e, this.id.replace('msg-', ''), $(window).width(), $(window).height());

                    if(e.which==2) {
                        // open message in new tab if message was middle clicked
                        server = '0';
                        folder = $('#msglist .foldersel').val();
                        uid = this.id.replace('msg-', '');
                        window.open('viewmsg/' + server + '/' + folder + '/' + uid + '/', '_blank');
                        
                        return true;
                    }

                    // show a modal dialog with an email msg
                    server = '0';
                    folder = $('#msglist .foldersel').val();
                    uid = this.id.replace('msg-', '');
                    dlgw = $(window).width() - 30;
                    dlgh = $(window).height() - 50;
                    console.log(dlgw, dlgh);
                    options = {
                        title: 'View Message',
                        closeable: true,
                        modal: true,
                        position: 'center',
                        width: dlgw,
                        height: dlgh
                    };

                    dw.dialog.viewmsg = $('<div></div>').append('body');
                    $(dw.dialog.viewmsg).load('viewmsg/' + server + '/' + folder + '/' + uid + '/').dialog(options);
                });
                $('tr.msg').hover(
                    function() { $(this).addClass('msghover'); },
                    function() { $(this).removeClass('msghover'); }
                );
            });
        };
        return this;
    };
}(jQuery));

dw.viewmsg.markmsg = function(how, server, folder, uid) {
    $.getJSON('action/mark'+how+'/?server='+server+'&folder='+folder+'&uid='+uid, function(j) {
        console.log(this, j);
    });
};

dw.dialog.compose = function() {
    $('body').append('<div id="compose" class="hidden"></div>');
    $('#compose').load('newmail/', function(j) {
        console.log(this, j);
        
        $('#compose').dialog({'width':'auto'});
    });
};

dw.dialog.prefs = function() {
    $('body').append('<div id="prefs" class="hidden"></div>');
    $('#prefs').load('prefs/', function(j) {
        console.log(this, j);
        
        $('#prefs').dialog({'width':'auto'});
        
        $('#tabs').tabs();
    });
};

dw.addSMTP = function(form) {
    
    console.log(form);
};

dw.sendMsg = function(form) {
    console.log(form);
};

dw.visfolders = [];
dw.updateFolderCounts = function(d) {
    console.log(d);
    
    dw.visfolders = [];
    $('#foldertree2  > ul > li > span').each(function(d) {
        // get a list of folders
        // TODO subfolders aren't getting their parent
        console.log(d, this, $(this).text());
        dw.visfolders.push($(this).text()); 
        console.log(dw.visfolders);
        // send list to server, it sends back unread counts per folder
        
    });
};