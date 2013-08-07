Campaign Manager
=============

Campaign Manager is a server that provides JSON fragments to be displayed by
the Firefox browser as part of product marketing and outreach.

Installing
----

System Requirements:
Please make sure the following packages are installed on the system:

gcc
gcc-c++
virtualenv
sqlite
libmysqlclient-dev
python-dev

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

For installation on a stand alone system (e.g. an AWS instance) where you
may wish the system to restart on reboot, you can easily get started by
doing the following.

If necessary, modify crontab.file to reflect correct path. If you already
have a crontab file, append the contents, else:

    $ crontab crontab.file

Authoring
----

https://$HOST:8080/author/1/

To create new announcements, you will need to connect via Persona with a
mozilla email address. If you wish to change this value, alter the
'auth.valid.domains' element in the campaign-local.ini configuration file.

Once connected, you will be presented with a form. Empty values are considered
"wild card" and will match all requests.

Requesting Announcements
----

https://$HOST:8080/announce/1/$PRODUCT/$CHANNEL/$VERSION/$PLATFORM?idle=$IDLE

An optional GET parameter of "idle" may be passed to indicate the number of
days the platform has been idle.

where:
*Product*
    name of the product for the notifications ('android')

*CHANNEL*
    Channel for the messages (e.g. 'firefox', 'aurora', 'nightly')

*VERSION*
    Channel version to target

*PLATFORM*
    Specific device platform (e.g. 'b2g-utx')

*IDLE*
    Optional days that the user agent has been idle.

Returns a JSON object containing

 {'announcements': [{url: _AnnounceURL_,
                     text: _AnnounceText_,
                     id: _uniqueId_,
                     title: _AnnounceTitle_},
                     ...
                   ]
 }

Redirection
---
https://$HOST:8080/redirect/1/$TOKEN
https://$HOST:8080/redirect/1/$LOCALE/$TOKEN

This will return a 302 to the correct destination for valid tokens, else 404

where:

*Token*
    Unique id

*Locale*
    Optional local information (e.g. 'en-US')

Returns a 302 to the actual URL.




Yay! You read it all. [Have a cookie!](http://jrconlin.com/cookies/)
