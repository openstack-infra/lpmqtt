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

import email
import imaplib2 as imaplib


class LPImapWatcher(object):

    def __init__(self, server, imap_user, imap_pass, folder='INBOX', ssl=False,
                 delete=False):
        super(LPImapWatcher, self).__init__()
        self.folder = folder
        if ssl:
            self.imap = imaplib.IMAP4_SSL(server)
        else:
            self.imap = imaplib.IMAP4(server)
        self.imap.login(imap_user, imap_pass)
        self.delete = delete

    def getEvents(self):
        self.imap.select(self.folder)
        events = self._find_new_email()
        return events

    def _process_bug(self, message):
        event = {}
        event['event-type'] = 'bug'
        event['commenters'] = message['X-Launchpad-Bug-Commenters'].split(' ')
        event['bug-reporter'] = message['X-Launchpad-Bug-Reporter']
        event['bug-modifier'] = message['X-Launchpad-Bug-Modifier']
        event['tags'] = message['X-Launchpad-Bug-Tags'].split(' ')
        bug_info = message['X-Launchpad-Bug'].split(';')
        for info in bug_info:
            clean_info = info.lstrip()
            key_value = clean_info.split('=')
            key = key_value[0]
            value = key_value[1]
            if key == 'product':
                event['project'] = value
            else:
                event[key] = value
        return event

    def _process_msg(self, data):
        event = {}
        message = email.message_from_string(data[1])
        if 'X-Generated-By' not in message or 'Launchpad' not in message[
            'X-Generated-By']:
            return event
        # Mark the message as read
        email_id = data[0].split()[0]
        self.imap.fetch(email_id, '(RFC822)')
        event_type = message['X-Launchpad-Notification-Type']
        if event_type == 'bug':
            event = self._proccess_bug(message)
        else:
            for header in message:
                if header.startswith('X-Launchpad'):
                    event[header] = message[header]
                event['body'] = message.get_payload()
        return event

    def _find_new_email(self):
        events = []
        typ, msg_ids = self.imap.search(None, "UNSEEN")
        for msg in msg_ids[0].split():
            typ, data = self.imap.fetch(msg, "(BODY.PEEK[HEADER])")
            output = self._process_msg(data, msg)
            if self.delete:
                self.imap.store(msg, '+FLAGS', '\\Deleted')
            events.append(output)
        if self.delete:
            self.imap.expunge()
        return events
