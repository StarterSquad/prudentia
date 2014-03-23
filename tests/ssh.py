import unittest
import json

from ansible import errors
from ansible import callbacks
from ansible import utils

from src.ssh import SshProvider
from src.domain import Box, Environment


class TestSshProvider(unittest.TestCase):
    def setUp(self):
        self.provider = SshProvider()
        self.test_box = Box('ssh-box', './dev.yml', 'ssh-hostname', '0.0.0.0')
        self.provider.add_box(self.test_box)

    def test_should_list_tag(self):
        tags = self.provider.tags[self.test_box.name]
        self.assertEqual(tags, ['all', 'one'])

    def test_box_does_not_exist_anymore(self):
        with open('./env/ssh/' + Environment.ENVIRONMENT_FILE_NAME, 'r') as fp:
            json_box = json.load(fp)[0]
        json_box['playbook'] = 'xxx.yml'
        with open('./env/ssh/' + Environment.ENVIRONMENT_FILE_NAME, 'w') as fp:
            json.dump([json_box], fp)
        self.provider_temp = SshProvider()
        self.assertEqual(self.provider_temp.tags, {})

    def tearDown(self):
        self.provider.remove_box(self.test_box)
