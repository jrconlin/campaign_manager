<!doctype html>
<%
    from time import (strftime, localtime)
    import json

    vers = pageargs.get('version', 1)
    land = pageargs.get('landing', '/author/%s/' % vers)
    config = pageargs.get('config', {})
    announcements = pageargs.get('announcements', [])
    author = pageargs.get('author', 'UNKNOWN')

%>
<html>
<head>
    <title>Welcome ${author}</title>
<link rel="stylesheet" type="text/css" href="/style.css" />
</head>
<body>
<header>
<h1>Campaign Admin Panel</h1>
<div id="control">
<button class="logout">Log out</button>
<!-- yep, this should be a REST get and display call. -->
</header>
<form id="new_item" action="${land}" method="POST">
<h2>New Item</h2>
<input type="hidden" name="author" value="${author}" />
<fieldset class="times">
<legend>When to show?</legend>
<label for="priority">Priority(0=lowest):</label><input type="number" name="priority" value="0" />
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
<label for="product">Product</label><input type="text" name="product" value="android" />
<label for="platform">Platform:</label><input type="text" name="platform" />
<label for="channel">Channel:</label><input type="text" name="channel" />
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
<div id="data">
<div class="head row">
<div class="delete">Delete?</div>
<div class="id">ID</div>
<div class="priority">Priority</div>
<div class="created">Created</div>
<div class="start_time">Start Time</div>
<div class="end_time">End Time</div>
<div class="idle_time">Idle Time</div>
<div class="lang">Language</div>
<div class="locale">Locale</div>
<div class="product">Product</div>
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
%for note in announcements:
<%
    dnote = dict(note);
    if dnote.get('start_time'):
        dnote['start_time'] = strftime(time_format, localtime(note.start_time))
    else:
        dnote['start_time'] = '<i>Now</i>'
    if dnote.get('end_time'):
        dnote['end_time'] = strftime(time_format, localtime(note.end_time))
    else:
        dnote['end_time'] = '<i>Forever</i>'
    if not dnote.get('idle_time'):
        dnote['idle_time'] = '<i>None</i>'
    if not dnote.get('lang'):
        dnote['lang'] = '<i>Everyone</i>'
    if not dnote.get('locale'):
        dnote['locale'] = '<i>Everywhere</i>'
    if not dnote.get('channel'):
        dnote['channel'] = '<i>All channels</i>'
    if not dnote.get('platform'):
        dnote['platform'] = '<i>All platforms</i>'
    if not dnote.get('version'):
        dnote['version'] = '<i>All versions</i>'
%>
<div class="record row">
    <div class="delete"><input type="checkbox" value="${note.id}"></div>
    <div class="id"><a href="/redirect/${vers}/${dnote['id']}">${dnote['id']}</a></div>
    <div class="priority">${dnote['priority']}</div>
<div class="created">${strftime(time_format, localtime(dnote['created']))}</div>
<div class="start_time">${dnote['start_time']}</div>
<div class="end_time">${dnote['end_time']}</div>
<div class="idle_time">${dnote['idle_time']} days</div>
<div class="lang">${dnote['lang']}</div>
<div class="locale">${dnote['locale']}</div>
<div class="product">${dnote['product']}</div>
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
                    document.location = "${land}";
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
            document.location="${land}";
        });
    });
    $("#delete").click(function() {
        deleteables=[]
        $("#existing .record .delete input").each(function () {
            if (this.checked){
               deleteables.push(this.value);
            }
        });
        console.debug(deleteables);
        $.ajax({url: "${land}",
            type: "POST",
            data: {"delete": deleteables},
            success: function(data, status, xhr) {
            document.location = "${land}";
            },
            error: function(xhr, status, error) {
                alert(error);
            }
        });
    });
</script>
</html>
