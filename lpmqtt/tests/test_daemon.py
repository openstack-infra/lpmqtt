# Copyright (c) 2016 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from lpmqtt import daemon
from lpmqtt.tests import base


class TestDaemonHelpers(base.TestCase):

    def test_process_event_full_topic(self):
        fake_event = {
            'project': 'tempest',
            'event-type': 'bug',
            'bug-number': '124321',
            'body': 'I am a email body',
        }
        msg, topic = daemon.process_event(fake_event, 'launchpad')
        self.assertEqual(json.dumps(fake_event), msg)
        self.assertEqual('launchpad/tempest/bug/124321', topic)

    def test_process_event_up_to_bug_number_no_event_type(self):
        fake_event = {
            'project': 'tempest',
            'bug-number': '124321',
            'body': 'I am a email body',
        }
        msg, topic = daemon.process_event(fake_event, 'launchpad')
        self.assertEqual(json.dumps(fake_event), msg)
        self.assertEqual('launchpad/tempest', topic)

    def test_process_event_no_bug_number(self):
        fake_event = {
            'project': 'tempest',
            'body': 'I am a email body',
            'event-type': 'bug',
        }
        msg, topic = daemon.process_event(fake_event, 'launchpad')
        self.assertEqual(json.dumps(fake_event), msg)
        self.assertEqual('launchpad/tempest/bug', topic)

    def test_process_event_no_project(self):
        fake_event = {
            'body': 'I am a email body',
            'event-type': 'bug',
            'bug-number': '124321',
        }
        msg, topic = daemon.process_event(fake_event, 'launchpad')
        self.assertEqual(json.dumps(fake_event), msg)
        self.assertEqual('launchpad', topic)
