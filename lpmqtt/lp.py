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
from email.header import decode_header
import re

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
        bug_tags = message['X-Launchpad-Bug-Tags']
        if bug_tags:
            event['tags'] = bug_tags.split(' ')
        subject = message['Subject']
        header_decode_out = decode_header(subject)
        subject = header_decode_out[0][0]
        bug_num_re_match = re.match('^\[(.*?)\]', subject)
        if not bug_num_re_match:
            print("Subject %s does not contain a parseable bug number"
                  % subject)
        else:
            bug_num_str = bug_num_re_match.group(0)
            event['bug-number'] = bug_num_str.split(' ')[1].rstrip(']')

        bug_info = message['X-Launchpad-Bug'].split(';')
        for info in bug_info:
            clean_info = info.lstrip()
            key_value = clean_info.split('=')
            if len(key_value) == 2:
                key = key_value[0]
                value = key_value[1]
                if key == 'product':
                    event['project'] = value
                else:
                    event[key] = value
        event['body'] = message.get_payload()
        return event

    def _process_msg(self, data):
        event = {}
        message = email.message_from_string(data[1])
        print('Initial filtering of Message ID: %s' % message['Message-Id'])
        generated_by = message['X-Generated-By']
        if not generated_by or 'Launchpad' not in generated_by:
            print('%s is not from LP' % message['Message-Id'])
            return event
        # Mark the message as read
        email_id = data[0].split()[0]
        typ, full_msg = self.imap.fetch(email_id, '(RFC822)')
        message = email.message_from_string(full_msg[0][1])
        print('Retrieved full message with id %s and marked as read'
              % message['Message-Id'])
        event_type = message['X-Launchpad-Notification-Type']
        if event_type == 'bug':
            event = self._process_bug(message)
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
            output = self._process_msg(data[0])
            if not output:
                continue
            if self.delete:
                self.imap.store(msg, '+FLAGS', '\\Deleted')
            events.append(output)
        if self.delete:
            self.imap.expunge()
        return events
