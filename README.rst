CampainManager
=============

Campaign Manager is a server that provides small HTML elements to be used
by the firefox browser as part of marketing and outreach.

Installing
----

System Requirements:
Please make sure the following packages are installed on the system:

gcc
virtualenv
sqlite

Once those packages are successfully installed:

$ make build

This will run the build steps required to get things started.
Please make sure that the build is successful and that all packages are installed.

$ cp campaign.ini campaign-local.ini
$ $EDITOR campaign-local.ini

(It is recommended that you copy campaign.ini to campaign-local.ini and
edit that file. This will prevent accidental updates of the configuration.)

You will need to change the line

 [who:plugin:browserid]
 audiences = Set.Domain.In.Ini.File

to be your current host address or machine name. This is used by Persona to
identify the correct recipient of the identity assertion. If this value does
not match your host, the assertion will fail.

Running
----

To run:

$ bin/pserve campaign-local.ini

This will start a server listening on the current host at port 8080. You
may change the port in use via the campaign-local.ini configuration file.

Authoring
----

https://$HOST:8080/author/

To create new announcements, you will need to connect via Persona with a
mozilla email address. If you wish to change this value, alter the
'auth.valid.domains' element in the campaign-local.ini configuration file.

Once connected, you will be presented with a form. Empty values are considered
"wild card" and will match all requests.

Requesting Announcements
----

https://$HOST:8080/announcements/$CHANNEL/$PLATFORM/$VERSION

An optional GET parameter of "idle" may be passed to indicate the number of
days the platform has been idle.

Redirection
---
https://$HOST:8080/redirect/$TOKEN
https://$HOST:8080/redirect/$LOCALE/$TOKEN

This will return a 302 to the correct destination for valid tokens, else 404

