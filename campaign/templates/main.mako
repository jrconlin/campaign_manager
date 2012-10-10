<!doctype html>
<%
    from time import (strftime, gmtime)
    import json

    config = pageargs.get('config', {})
    notes = pageargs.get('notes', [])
    author = pageargs.get('author', 'UNKNOWN')

%>
<html>
<head>
    <title>Welcome ${author}</title>
<link rel="stylesheet" type="text/css" href="/style.css" />
</head>
<body>
<header>
<h1>Lovenote Admin Panel</h1>
<div id="control">
<button class="logout">Log out</button>
<!-- yep, this should be a REST get and display call. -->
</header>
<form id="new_item" action="/author/" method="POST">
<h2>New Item</h2>
<input type="hidden" name="author" value="${author}" />
<fieldset class="times">
<legend>When to show?</legend>
<label for="start_time">Start time:</label><input type="datetime-local" name="start_time" value="" />
<label for="end_time">End time:</label><input type="datetime-local" name="end_time" value="" />
<label for="idle_time">Idle time(days):</label><input type="number" name="idle_time" value="0" />
</fieldset>
<fieldset class="note">
<legend>What should they see?</legend>
<label for="title">Title:</label><input type="text" name="title" />
<label for="dest_url">Destination URL:</label><input type="text" name="dest_url" />
<label for="note">Note:</label><input type="text" name="note" />
</fieldset>
<fieldset class="locale">
<legend>Who should see?</legend>
<label for="lang">Language:</label><input type="text" name="lang" length="2" value="en" />-
<label for="locale">Locale:</label><input type="text" name="locale" length="2" value="US" />
</fieldset>
<fieldset class="platform">
<legend>On what?</legend>
<label for="platform">Platform:</label><select name="platform">
<option name="all" value="">All versions</option>
%for platform in ['all','android','b2g','mac','pc']:
<option name="${platform}">${platform}</option>
%endfor
</select>
<label for="channel">Channel:</label><select name="channel">
%for channel in ['all', 'firefox','beta','aurora','nightly']:
<option name="${channel}">${channel}</option>
%endfor
</select>
<label for="version">Version:</label><input type="text" name="version" />
</fieldset>
<button type="submit">Create</button>
<button type="clear">Clear</button>
</form>
<div id="existing">
<h2>Existing Records</h2>
<div class="control">
<button id="select_all" name="select_all">Select all</button>
<button id="clear" name="clear_all">Clear selected</button>
<button id="delete" name="delete">Delete Selected</button>
</div>
<div class="data">
    <div class="head row">
<div class="delete">Delete?</div>
<div class="id">ID</div>
<div class="created">Created</div>
<div class="start_time">Start Time</div>
<div class="end_time">End Time</div>
<div class="idle_time">Idle Time</div>
<div class="lang">Language</div>
<div class="locale">Locale</div>
<div class="platform">Platform</div>
<div class="channel">Channel</div>
<div class="version">Version</div>
<div class="author">Author</div>
<div class="note">Note</div>
<div class="dest_url">Destination URL</div>
</div>
<%
    time_format = '%Y %b %d - %H:%M:%S UTC'
    %>
    <!-- Wanna guess what ougth to be done as a rest call? hint: -->
%for note in notes:
<%
    dnote = dict(note);
    if 'start_time' in note:
        dnote['start_time'] = strftime(time_format, gmtime(note.start_time))
    else:
        dnote['start_time'] = '<i>Now</i>'
    if 'end_time' in note:
        dnote['end_time'] = strftime(time_format, gmtime(note.end_time))
    else:
        dnote['end_time'] = '<i>Forever</i>'
    if not 'idle_time' in note:
        dnote['idle_time'] = '<i>None</i>'
    if not 'lang' in note:
        dnote['lang'] = '<i>Everyone</i>'
    if not 'locale' in note:
        dnote['locale'] = '<i>Everywhere</i>'
    if not 'channel' in note:
        dnote.channel = '<i>All channels</i>'
    if not 'platform' in note:
        dnote.platform = '<i>All platforms</i>'
    if not 'version' in note:
        dnote.version = '<i>All versions</i>'
%>

<div class="data row">
    <div class="delete"><input type="checkbox" value="sel_${note.id}"></div>
<div class="id">${dnote['id']}</div>
<div class="created">${strftime(time_format, gmtime(dnote['created']))}</div>
<div class="start_time">${dnote['start_time']}</div>
<div class="end_time">${dnote['end_time']}</div>
<div class="idle_time">${dnote['idle_time']} days</div>
<div class="lang">${dnote['lang']}</div>
<div class="locale">${dnote['locale']}</div>
<div class="platform">${dnote['platform']}</div>
<div class="channel">${dnote['channel']}</div>
<div class="version">${dnote['version']}</div>
<div class="author">${dnote['author']}></div>
<div class="note">${dnote['note']}</div>
<div class="dest_url">${dnote['dest_url']}</div>
</div>
%endfor
</div>
<footer>

</footer>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js" type="text/javascript"></script>
<script id='bidjs' src="https://browserid.org/include.js" type="text/javascript"></script>
<script type="text/javascript">
    $(".logout").bind("click", function(e) {
            $.ajax({url: "/logout/",
                type: "DELETE",
                contentType: "application/javascript",
                success: function(data, status, xhr) {
                    document.location = "/author/";
                    },
                error: function(xhr, status, error) {
                    console.error(status);
                    console.error(error);
                    $(".logout").disable();
                    }
            });
    });
    $("#bidjs").ready(function() {
            $(".logout").click(function(){
                alert('clicky');
            navigator.id.logout();
            $.cookie("campaign", null, {path: "/"});
            document.location="/author/";
            })
    });
</script>
</html>
