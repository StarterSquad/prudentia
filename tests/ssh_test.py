import unittest
import os

# this import workaround an issue related with circular dependencies
# https://groups.google.com/forum/#!msg/ansible-devel/wE7fNbGyWbo/IvuUpbJI4aoJ
import ansible.playbook

from src.ssh import SshProvider
from src.domain import Box


class TestSshProvider(unittest.TestCase):
    def setUp(self):
        self.provider = SshProvider()

    def test_should_list_tag(self):
        tests_path = os.path.dirname(__file__)
        e_box = Box('ssh-box', tests_path + '/dev.yml', 'ssh-hostname', '0.0.0.0')
        self.provider.load_tags(e_box)
        self.assertEqual(self.provider.tags.has_key(e_box.name), True)
        self.assertEqual(self.provider.tags[e_box.name], ['all', 'one'])

    def test_should_not_list_tags_if_box_not_exists(self):
        ne_box = Box('ssh-box-2', 'xxx.yml', 'ssh-hostname', '0.0.0.0')
        self.provider.load_tags(ne_box)
        self.assertEqual(self.provider.tags.has_key(ne_box.name), False)
