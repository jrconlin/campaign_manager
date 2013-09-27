<!DOCTYPE html>
<%
from time import (strftime, localtime)

users = pageargs.get('users', [])
sponsor = pageargs.get('user', '')
error = pageargs.get('error', '')
land = pageargs.get('land', "/admin/")
time_format = '%a, %d %b %Y - %H:%M:%S GMT'

%>
<html>
<head>
<title>Account management</title>
<link rel="stylesheet" type="text/css" href="/static/style.css" />
<link rel="stylesheet" type="text/css" href="http://www.mozilla.org/tabzilla/media/css/tabzilla.css" />
</head>
<body>
    <header>
        <h1> User Management</h1>
    <div class="control">
        <a class="button" href="/author/1/">Campaigns</a>
    </div>
    </header>
    <div class="new_user">
<h2>New User</h2>
<form id="new_user" action="${land}" method="POST">
    <label for="user">User Email:<input name="user"></label>
    % if error is not None and len(error) > 0:
<div class="error">${error}</div>
% endif
<button class="button" type="submit" alt="add">Add User</button>
<form>
    <div>
        <h2>Users:</h2>
<table class="existing_users">
<tr><th>User:</th><th>Added by:</th><th>On:</th><th><th></tr>
% for user in users:
<%  duser = dict(user) %>
<tr>
<td class="user">${user['email']}</td>
<td class="sponsor">${user['sponsor']}</td>
<td class="date">${strftime(time_format, localtime(user['date']))}</td>
<td class="rm">
    % if sponsor != user['email'] and user['sponsor'] is not None:
<button class="button remove" value="${user['id']}" name="remove">Remove</button>
% endif
</td>
</tr>
% endfor
</table>
</body>
</html>
