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
dw.msglist = {};
dw.dialog = {};

$(document).ready(function() {
    //console.log('doc ready');
    
    // refresh msg list periodically
    // TODO stuff a configurable time into the body or something
    refid = window.setInterval(function(){
        //console.log('msglist refresh');
        $('#msglist .foldersel').change();
    }, 5*60*1000);
    window.setInterval(dw.updateFolderCounts, 5*60*1000);

    dw.msgtable = $('#msglist').srvDatatable();

    // folder tree -- https://github.com/Erffun/JsonTree
    $.getJSON('json/folderlist2/?server=0&parent=', function(data) {
        //console.log('fl2', data);
        $('#foldertree2').jsonTree(data, {
            mandatorySelect: true,
            lazyLoad: true,
            lazyRequestUrl: 'json/folderlist2/?server=0',
            lazySendParameterName: 'parent',
            onSelect: function(selid, selli, clickedli) {
                //console.log("ft2 onSelect", selid, selli, clickedli);
                //console.log(selli.attr('value'));
                $('.foldersel').val(selli.attr('value'));
                $('#msglist .foldersel').change();
                $('#foldertree2 i').on('click', dw.updateFolderCounts); // HACK treefolder should have a onExpand
                dw.updateFolderCounts();
            },
        });
        dw.updateFolderCounts();
        $('#foldertree2 i').on('click', dw.updateFolderCounts); // HACK treefolder should have a onExpand
    });
    
    // hide the spinner
    $('#searchOptions').hide();
    $('#spinner').hide();
    $('#serverMessage').hide();
});

/*
 * jQuery server side datatable plugin
 *
 * Copyright (c) 2009-2014 Brian Jackson <iggy@theiggy.com>
 *
 * A datatable plugin that does all the searching, sorting, pagination, etc. on
 * the server. This was written mainly for Simone, which uses an IMAP
 * backend. The IMAP server will almost always be better at sorting, searching,
 * etc.
 *
 * Licensed under same license as Simone (i.e. BSD)
 */
;(function($) {
    $.fn.srvDatatable = function() {
        //console.log('start srvDatatable', this, $(this));
        var $cnt = $(this);

        // html used for the navigation above the message list
        var navht = ' \
<form class="msgnav" action="msglist/" method="get" onSubmit="return false;"> \
    <input type="text" readonly="readonly" value="INBOX" class="foldersel ui-widget" /> \
    <button id="msgnav-firstpage"\
        class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only"> \
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
    <button id="lastPageButton" \
        class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only" \
        onclick="$(\'#msglist .pagesel\').lastPage(); return false;"> \
            <span class="ui-icon ui-icon-arrowthickstop-1-e"></span> \
    </button> \
    <select title="Messages To Show Per Page" \
        class="perpagesel ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only"> \
        <option selected="selected">10</option> \
        <option>20</option> \
        <option>40</option> \
        <option>50</option> \
    </select> \
    <select title="Sort Direction" \
        class="sortordersel ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only"> \
        <option>Asc</option> \
        <option selected="selected">Desc</option> \
    </select> \
    <input id="msgsearch" type="text" class="ui-widget" /> \
    <button id="searchsubmit" \
        class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only"> \
        <span class="ui-button">Search</span> \
    </button> \
</form> \
            ';
// TODO filters (unread, marked, etc)
        var tableht = ' \
<table class="ui-datatable" style="width:100%"> \
    <tr class="ui-tabs-nav ui-helper-reset ui-widget-header ui-corner-all"> \
        <th><input type="checkbox" /></th> \
        <th>Subject</th> \
        <th>From</th> \
        <th style="width:13em">Date</th> \
        <th>Size</th>\
    </tr> \
</table>';

        $cnt.append(navht);

        $cnt.append(tableht);

        //$('#msglist th').addClass('ui-corner-all');

        var $foldersel = $cnt.find('.foldersel'),
            $pagesel = $cnt.find('.pagesel'),
            $perpagesel = $cnt.find('.perpagesel'),
            $sortordersel = $cnt.find('.sortordersel'),
            $tbl = $cnt.find('table'),
            $msgsearch = $cnt.find('#msgsearch'),
            $searchsubmit = $cnt.find('#searchsubmit');

        $foldersel.change(update);
        $pagesel.change(update);
        $perpagesel.change(update);
        $sortordersel.change(update);
        $searchsubmit.click(update);
        $('#msgnav-firstpage').on('click', firstPage);

        update();
        
        // setup the checkboxes
        $('#msglist th input[type="checkbox"]').click(function(event) {
            // clicked the table header checkbox, so check all the visible boxes
            //console.log('th checkbox click', event);
            isChecked = event.currentTarget.checked;
            $('#msglist input[type="checkbox"]').each(function(index) {
                $(this)[0].checked = isChecked;
            });
        });

        function getUrl() {
            var url = $cnt.find('.msgnav').attr('action') + // form action specifies the base of the url
            '0/' + // server
            $foldersel.val() + '/' + // folder
            $pagesel.val() + '/' + // page
            $perpagesel.val() + '/' + // msgs per page
            'date/'+
            $sortordersel.val().charAt(0) + '/' + // sort order
            $msgsearch.val() + '/'; // search terms
            
            //console.log('getURL()', url);
            return url;
        };
        
        function firstPage(e) {
            console.log("first page", this);
            e.preventDefault();
            $pagesel.val('1');
            update();
        };
        function prevPage(e) {
            console.log("prev page", this);
            e.preventDefault();
            $pagesel.val($pagesel.val()-1);
            update();
        };
        function nextPage(e) {
            console.log("next page", this);
            e.preventDefault();
            $pagesel.val($pagesel.val()+1);
            update();
        };
        function lastPage(e) {
            console.log("last page", this);
            e.preventDefault();
            $pagesel.val('1');
            update();
        };
        function update(event) {
            event && event.preventDefault();
            $.getJSON(getUrl(), function(data) {
                //console.log('get msglist callback', data);
                
                if(data['status'] == 'ERROR') {
                    $('#serverMessage').html('Error searching: <br />' + data['message']);
                    $('#serverMessage').removeClass('ui-state-highlight').addClass('ui-state-error').show().delay(5000).hide(500);
                    return;
                }

                // fill pagesel
                $pagesel.empty();
                //console.log(data['totalmsgs'], $perpagesel.val(), 
                //    Math.ceil(data['totalmsgs'] / $perpagesel.val()));
                $('#lastPageButton').click(function(event) {
                    console.log('lastPageButton click', event);
                    $pagesel.val(Math.max(Math.ceil(data['totalmsgs'] / $perpagesel.val()), 1));
                    $pagesel.change();
                    event.preventDefault();
                });
                for(var i = 1 ; i <= Math.max(Math.ceil(data['totalmsgs'] / $perpagesel.val()), 1) ; i++) {
                    var selht = '';
                    if($sortordersel.val().charAt(0) == "A" && i == Math.ceil(data['stop']/$perpagesel.val()))
                        selht = ' selected="selected"';
                    if($sortordersel.val().charAt(0) == "D" && i == Math.floor(data['totalmsgs']/$perpagesel.val() - data['stop']/$perpagesel.val()) + 1)
                        selht = ' selected="selected"';
                    $pagesel.append('<option'+selht+'>' + i + '</option>');
                }

                // fill the msglist table
                $tbl.find('tr:not(:first)').remove();
                //console.log(data['msglist'].length);
                for(var uid in data['msglist']) {
                    msg = data['msglist'][uid];
                    //console.log('168', uid, msg);
                    var rclass = '';
                    //var rclass = 'odd ui-state-highlight';
                    //if(uid % 2 == 0)
                    //    rclass = 'even';
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
                    //console.log("regex5", r.exec(msg['from']));

                    $tbl.append(' \
<tr class="msg ' + rclass + '"> \
    <td><input type="checkbox" value="'+msg['uid']+'" id="'+msg['uid']+'-cb" /></td> \
    <td class="subject' + fclass + '" id="msg-' + msg['uid'] + '">' + msg['subject'] + '</td> \
    <td><a href="mailto:'+msg['from'][1]+'">' + msg['from'][0] + '</a></td> \
    <td>' + msg['date'] + '</td> \
    <td>' + Math.round((msg['size']/1024)*10)/10 + 'K</td> \
</tr> \
                    ');
                }

                // msg listener
                $('tr.msg td.subject').click(function(e) {
                    //console.log('subject click', this, e, this.id.replace('msg-', ''), $(window).width(), $(window).height());

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
                    //console.log(dlgw, dlgh);
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
                    
                    $(this).parent().removeClass('msgunseen');
                    $(this).parent().addClass('msgseen');
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

// mark single message from msgview
dw.viewmsg.markmsg = function(e, how, server, folder, uid) {
    //console.log(e, how, server, folder, uid, this);
    e.preventDefault();
    $.getJSON('action/mark'+how+'/?server='+server+'&folder='+folder+'&uid='+uid, function(j) {
        //console.log('markmsg json callback', this, j);
        $('#msglist .foldersel').change();
    });
};
// mark multiple messages from the msglist
dw.msglist.markmsg = function(e, how, server) {
    //console.log(e, how, server, this);
    e.preventDefault();
    folder = $('#msglist .foldersel').val();
    //uids = $('#msglist tr > td input:checked').map(function(){return $(this).val();});
    uids = []
    $('#msglist tr > td input:checked').each(function(idx, el) {
        //console.log('i', idx, 'e', el, 't', this, 'jt', $(this));
        uids.push($(el).val());
    });
    uidso = {'uids': uids}
    //console.log(uidso, uids);
    $.getJSON('action/mark'+how+'/?server='+server+'&folder='+folder+'&'+$.param(uidso), function(j) {
        //console.log('markmsg json callback', this, j);
        $('#msglist .foldersel').change();
    });
    
    $('#msglist th input[type="checkbox"]').prop('checked', false);
    dw.updateFolderCounts();
};
// move or copy multiple messages from the msglist
dw.msglist.mc = function(e, how) {
    //console.log(e, how);
    e.preventDefault();
    curfolder = $('#msglist .foldersel').val();
    newfolder = $('#checkedFolder').val();
    uids = []
    $('#msglist tr > td input:checked').each(function(idx, el) { uids.push($(el).val()); });
    uidso = {'uids': uids}
    //console.log(uidso, uids);
    $.getJSON('action/mc'+how+'/?server=0&folder='+curfolder+'&newfolder='+newfolder+'&'+$.param(uidso), function(j) {
        //console.log('markmsg json callback', this, j);
        $('#msglist .foldersel').change();
    });
    
    $('#msglist .foldersel').delay(3000).change();
    $('#msglist th input[type="checkbox"]').prop('checked', false);
};

// load a new compose dialog
dw.dialog.compose = function(event) {
    console.log('open compose dialog');
    event && event.preventDefault();
    $('#compose').length || $('body').append('<div id="compose" class="hidden"></div>');
    $('#compose').load('newmail/', function(j) {
        console.log('compose callback', this, j);
        
        // Set a few style bits here that are calculated
        // FIXME these values are pretty much pulled out of nowhere
        $('#compose input[type=text]').width($(window).width()/2);
        $('#editor').width($(window).width()-130);
        $('#editor').height($(window).height()-300);
        
        $('#compose').dialog({'width':$(window).width()-30, 'height':$(window).height()-50});
    });
};
dw.dialog.reply = function(event, who, server, folder, uid) {
    console.log('dw.dialog.reply', event, who, server, folder, uid);
    $('#compose') || $('body').append('<div id="compose" class="hidden"></div>');
    var data = {
        'who': who,
        'server': server,
        'folder': folder,
        'uid': uid
    }
    $('#compose').load('replymail/', data, function(j) {
        console.log('reply callback', this, j);
        
        // Set a few style bits here that are calculated
        // FIXME these values are pretty much pulled out of nowhere
        $('#compose input[type=text]').width($(window).width()/2);
        $('#editor').width($(window).width()-130);
        $('#editor').height($(window).height()-300);
        
        $('#compose').dialog({'width':$(window).width()-30, 'height':$(window).height()-50});
    });
};

dw.dialog.prefs = function(event) {
    event && event.preventDefault();
    $('body').append('<div id="prefs" class="hidden"></div>');
    $('#prefs').load('prefs/', function(j) {
        console.log('prefs dialog callback', this, j);
        
        $('#prefs').dialog({'width':'auto'});
        
        $('#prefstabs').tabs();
    });
};

dw.addSMTP = function(event, el) {
    
    console.log('addSMTP', event, el);
};

dw.sendMail = function(event, el) {
    event.preventDefault();
    //console.log('sendMail', event, el, $(el));
    
    form = $('#compose form');
    fs = $(form).serialize();
    //console.log(fs);
    $.post("send/", fs, function(data) {
        //console.log(data);
        j = $.parseJSON(data);
        if(j.status == "SUCCESS") {
            $('#sendMailMsg').addClass('ui-state-highlight');
        } else if(j.status == "ERROR") {
            $('#sendMailMsg').addClass('ui-state-error');
        }
        $('#sendMailMsg').html('Status: ' + j.status + '<br />' + j.message);
    })
};

dw.visfolders = [];
dw.updateFolderCounts = function(d) {
    //console.log('updateFolderCounts', d);
    
    dw.visfolders = [];
    $('#foldertree2 ul > li').each(function(d) {
        // get a list of folders
        // TODO subfolders aren't getting their parent
        //console.log(d, this, $(this).text(), $(this).attr('value'));
        dw.visfolders.push($(this).attr('value')); 
        //console.log(dw.visfolders);
    });
    // send list to server, it sends back unread counts per folder
    req = {'server':0, 'folders':dw.visfolders};
    $.post('json/unread/', req, function(data, status, jhx){
        //console.log('updateFolderCounts json callback', data, status);
        // FIXME handle multiple servers
        for(var folder in data['servers']['0']){
            //console.log(folder);
            //console.log($('#foldertree2 li[value="'+folder+'"]'));
            var count = '';
            if(data['servers']['0'][folder] > 0)
                count = '(' + data['servers']['0'][folder] + ')';
            if($('#foldertree2 li[value="'+folder+'"] > span > b').size() > 0)
                $('#foldertree2 li[value="'+folder+'"] > span > b').html(count);
            else
                $('#foldertree2 li[value="'+folder+'"] > span').append(' <b>' + count + '</b>');
        }
    }, 'json');
    $('#foldertree2 i').on('click', dw.updateFolderCounts); // HACK treefolder should have a onExpand
};

// make Django's CSRF framework happy
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});
