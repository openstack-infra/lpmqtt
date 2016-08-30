# Copyright 2016 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import sys

import paho.mqtt.publish as publish
from six.moves import configparser

from lpmqtt import lp


class PushMQTT(object):
    def __init__(self, hostname, port=1883, client_id=None,
                 keepalive=60, will=None, auth=None, tls=None):
        self.hostname = hostname
        self.port = port
        self.client_id = client_id
        self.keepalive = 60
        self.will = will
        self.auth = auth
        self.tls = tls

    def publish_single(self, topic, msg):
        publish.single(topic, msg, hostname=self.hostname,
                       port=self.port, client_id=self.client_id,
                       keepalive=self.keepalive, will=self.will,
                       auth=self.auth, tls=self.tls)

    def publish_multiple(self, topic, msg):
        publish.multiple(topic, msg, hostname=self.hostname,
                         port=self.port, client_id=self.client_id,
                         keepalive=self.keepalive, will=self.will,
                         auth=self.auth, tls=self.tls)


def process_event(event, base_topic):
    pieces = [base_topic]
    if 'project' in event:
        pieces.append(event['project'])
        if 'event_type' in event:
            pieces.append(event['event-type'])
            if 'bug-number' in event:
                pieces.append(event['bug-number'])
    topic = "/".join(pieces)
    msg = json.dumps(event)
    return msg, topic


def main():
    config = configparser.ConfigParser()
    config.read(sys.argv[1])

    # Configure MQTT Connection
    if config.has_option('mqtt', 'port'):
        mqtt_port = config.get('mqtt', 'port')
    else:
        mqtt_port = 1883
    if config.has_option('mqtt', 'keepalive'):
        keepalive = config.get('mqtt', 'keepalive')
    else:
        keepalive = 60
    # Configure MQTT auth
    auth = None
    if config.has_option('mqtt', 'username'):
        mqtt_username = config.get('mqtt', 'username')
    else:
        mqtt_username = None
    if config.has_option('mqtt', 'password'):
        mqtt_password = config.get('mqtt', 'password')
    else:
        mqtt_password = None
    if mqtt_username:
        auth = {'username': mqtt_username}
        if mqtt_password:
            auth['password'] = mqtt_password
    base_topic = config.get('mqtt', 'base_topic')

    mqttqueue = PushMQTT(
        config.get('mqtt', 'hostname'),
        port=mqtt_port,
        keepalive=keepalive,
        auth=auth)

    # IMAP email settings
    imap_server = config.get('imap', 'hostname')
    imap_user = config.get('imap', 'username')
    imap_password = config.get('imap', 'password')
    if config.has_option('imap', 'use_ssl'):
        imap_ssl = config.getboolean('imap', 'use_ssl')
    else:
        imap_ssl = False

    if config.has_option('imap', 'folder'):
        imap_folder = config.get('imap', 'folder')
    else:
        imap_folder = 'INBOX'

    if config.has_option('imap', 'delete-old'):
        imap_delete = config.getboolean('imap', 'delete-old')
    else:
        imap_delete = False

    launchpad = lp.LPImapWatcher(imap_server, imap_user, imap_password,
                                 folder=imap_folder, ssl=imap_ssl,
                                 delete=imap_delete)
    while True:
        events = launchpad.getEvents()
        for event in events:
            msg, topic = process_event(event, base_topic)
            mqttqueue.publish_single(topic, msg)
        launchpad.imap.idle()

if __name__ == "__main__":
    main()
