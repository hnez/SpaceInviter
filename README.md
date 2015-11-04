Space Inviter
=============

A Python/WSGI based Web Application for
managing smallish events like birtday partys.
Featurig individual token based invitations,
a chat system and a graphical estimation
of the number of participants.

Please note, that SpaceInviter was written
as an exercise in writing a REST Api
and has not yet evolved into a production ready product.

Dependencies
------------

SpaceInviter is built using bottle.py for
wsgi abstraction an SQLObject for database
abstraction.

To install them on debian based distributions type:

    $ sudo aptitude install python-{sqlobject,bottle}

Usage
-----

To test SpaceInviter run:

    $ ./inviter.py sqlite:///tmp/testos.db

Screenshot
----------

![Application screenshot](screenshots/event.png?raw=true "SpaceInviter in action")