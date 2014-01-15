<!DOCTYPE html>
<%
    # This Source Code Form is subject to the terms of the Mozilla Public
    # License, v. 2.0. If a copy of the MPL was not distributed with this
    # file, You can obtain one at http://mozilla.org/MPL/2.0/.

    vers = pageargs.get('version', '1')
    land = pageargs.get('landing', '/author/%s/' % vers)
    audience = pageargs.get('audience', 'localhost')
    user = pageargs.get('user', '');

%>
<html>
    <head>
        <title>Please log in</title>
        <link rel="stylesheet" type="text/css" href="/static/style.css" />
        <meta charset="utf-8" />
  </head>
  <body data-user='${user}'>
      <hgroup>
      <h2>Please Log in</h2>
      </hgroup>
      <div id="browserid"><img src="//login.persona.org/i/sign_in_grey.png" id="signin"></div>
      <footer>&nbsp;</footer>
      <script src="//ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js" type="text/javascript"></script>
      <script id='bidjs' src="//login.persona.org/include.js" type="text/javascript"></script>
      <script type="text/javascript">
          $(function() {
            email = '';
            if ($('body').data('user')) {
                email = $('body').data('user').email;
            }
            navigator.id.watch(
                { loggedInUser: email,
                  onlogout: function() { },
                  onlogin: function(assertion) {
                      document.getElementsByTagName('body')[0].style.cursor='auto';
                      var form = $("<form method='POST' action='${land}' >" +
                      "<input type='hidden' name='assertion' value='" + assertion +
                      "'/><input type='hidden' name='audience' value='${audience}'>" +
                      "</form>").appendTo('#browserid');
                      form.submit();
                      }});
    $('#signin').click(function(){
        document.getElementsByTagName('body')[0].style.cursor='wait';
        navigator.id.request();
    });
    $('#bidjs').ready(function() {
        $('#signin').attr('src', "//login.persona.org/i/sign_in_blue.png");
    })
    });
      </script>
  </body>
</html>
