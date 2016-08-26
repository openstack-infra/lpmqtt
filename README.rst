======
lpmqtt
======

lpmqtt, like its name implies, is a tool for publish a launchpad event stream
into MQTT. It will publish all the capture events from the lp emails over imap
and publish them to MQTT

MQTT Topics
===========
lpmqtt will push gerrit events to topics broken by project and event type.
The formula used is::

  <base topic>/<bugs or blueprints>/<number>


Configuration
=============
There are a few required pieces of information to make lpmqtt work properly.
These settings are specified in the config file.
