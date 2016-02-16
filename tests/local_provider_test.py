import unittest
import os

from mock import patch
from prudentia.domain import Box
from prudentia.local import LocalProvider


class TestLocalProvider(unittest.TestCase):
    def setUp(self):
        self.tests_path = os.path.dirname(os.path.realpath(__file__))
        self.provider = LocalProvider()

    def test_provision_sample_task(self):
        r_box = Box('local-testbox', self.tests_path + '/prudentia_vars.yml', 'tasks-host', '127.0.0.1')
        self.provider.add_box(r_box)

        self.provider.provision(r_box, [])
        self.assertEqual(self.provider.provisioned, True)

        self.provider.provision(r_box, ['uname'])
        self.assertEqual(self.provider.provisioned, True)

        self.provider.remove_box(r_box)

    def test_should_list_tag(self):
        e_box = Box('simple-box', './uname.yml', 'hostname', '0.0.0.0')
        self.provider.load_tags(e_box)
        self.assertEqual(self.provider.tags.has_key(e_box.name), True)
        # the tag 'echo' is not returned since Ansible introduced dynamic includes
        # might be fixed in some next 2.x version
        # self.assertEqual(self.provider.tags[e_box.name], ['one', 'echo'])
        self.assertEqual(self.provider.tags[e_box.name], ['one'])

    def test_should_not_list_tags_if_box_not_exists(self):
        ne_box = Box('simple-box-2', 'xxx.yml', 'ssh-hostname', '0.0.0.0')
        self.provider.load_tags(ne_box)
        self.assertEqual(self.provider.tags.has_key(ne_box.name), False)

    def test_gather_facts(self):
        box = Box('simple-box', './uname.yml', 'hostname', '0.0.0.0')
        self.assertTrue(self.provider.facts(box, '*mb'))

    def test_register(self):
        def input_side_effect(*args):
            input_values = {'playbook path': './uname.yml', 'box name': 'b_name'}
            return input_values[args[0]]

        with patch('prudentia.utils.io.input_value') as iv:
            iv.side_effect = input_side_effect

            self.provider.register()
            self.assertNotEqual(self.provider.get_box('b_name'), None)
