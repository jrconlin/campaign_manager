<!DOCTYPE html>
<%
    # This Source Code Form is subject to the terms of the Mozilla Public
    # License, v. 2.0. If a copy of the MPL was not distributed with this
    # file, You can obtain one at http://mozilla.org/MPL/2.0/.

    land = pageargs.get('landing', '/author/')
    audience = pageargs.get('audience', 'localhost')
%>
<html>
    <head>
        <title>Please log in</title>
        <link rel="stylesheet" type="text/css" href="/style.css" />
  </head>
  <body>
      <hgroup>
      <h2>Please Log in</h2>
      </hgroup>
      <div id="browserid"><img src="https://browserid.org/i/sign_in_grey.png" id="signin"></div>
      <footer>&nbsp;</footer>
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js" type="text/javascript"></script>
      <script id='bidjs' src="https://browserid.org/include.js" type="text/javascript"></script>
      <script type="text/javascript">
          $(function() {
             $('#signin').click(function(){
              document.getElementsByTagName('body')[0].style.cursor='wait';
              navigator.id.getVerifiedEmail(function(assertion) {
                  document.getElementsByTagName('body')[0].style.cursor='auto';
                  var form = $("<form method='POST' action='${land}' >" +
                      "<input type='hidden' name='assertion' value='" + assertion +
                      "'/><input type='hidden' name='audience' value='${audience}'>" +
                      "</form>").appendTo('#browserid');
                  form.submit();
              })
              });
             $('#bidjs').ready(function() {
                 $('#signin').attr('src', "http://browserid.org/i/sign_in_blue.png");
                 })
      });
      </script>
  </body>
</html>
