======
lpmqtt
======

lpmqtt, like its name implies, is a tool for publish a launchpad event stream
into MQTT. It will publish all the capture events from the lp emails over imap
and publish them to MQTT

MQTT Topics
===========
lpmqtt will push launchpad events to topics broken by project and event type.
The formula used is::

  <base topic>/<project>/<bugs, blueprints, or other event type>/<bug number>

However only the base topic is a guaranteed field. Depending on the emails sent
by launchpad some of the other fields may not be present. In those cases the
topic will start from the base topic and will use fields moving towards the
right until one is missing.


Configuration
=============
There are a few required pieces of information to make lpmqtt work properly.
These settings are specified in the config file.

IMAP
----
To configure lpmqtt to listen to your imap server you need to provide 3 pieces
of information in the *[imap]* section

 * **hostname** - The hostname for the imap server to connect to
 * **username** - The username to connect with
 * **password** - The password to use

There are also a number of optional settings you can use depending on the
configuration of the imap server you're connecting to:

 * **use_ssl** - Set this to *True* to establish an imaps connection with ssl
 * **folder** - Specify a mailbox/folder to watch for message from launchpad.
                If one is not specified *INBOX* will be used
 * **delete-old** - Set this to *True* to have lpmqtt delete messages after it
                    finishes processing them. By default it will just mark them
                    as read.

MQTT
----
Just as with imap there are a few required options for talking to MQTT, which
is the other axis of communication in lpmqtt. The options for configuring MQTT
communication go in the *[mqtt]* section. The 2 required options are:

 * **hostname** - The hostname for the MQTT broker
 * **base_topic** - The base topic name to use for the gerrit events

There are also a couple optional settings for communicating with mqtt that you
can set:

 * **port** - The port to communicate to the MQTT broker on. By default this
              is set to 1883, the default MQTT port. This only needs to be set
              if your broker uses a non-default port.
 * **keepalive** - Used to set the keepalive time for connections to the MQTT
                   broker. By default this is set to 60 seconds.
 * **username** - Used to set the auth username to connect to the MQTT broker
                  with.
 * **password** - Used to set the auth password to connect to the MQTT broker
                  with. A username must be set for this option to be used.
