from os import path
import unittest

from mock import patch
from prudentia.domain import Box
from prudentia.ssh import SshCli


class TestSshCli(unittest.TestCase):
    def setUp(self):
        self.tests_path = path.dirname(path.realpath(__file__))
        self.cli = SshCli()

    def test_define_box(self):
        expected_box = Box(
            name='ssh-test-box',
            playbook=path.join(self.tests_path, 'uname.yml'),
            hostname='localhost',
            ip='1.2.3.4',
            remote_user='nobody',
            remote_pwd=''
        )

        def input_side_effect(*args, **kwargs):
            input_values = {
                'playbook path': 'uname.yml',
                'box name': expected_box.name,
                'instance address or inventory': '1.2.3.4',
                'remote user': 'nobody',
                'password for the remote user': ''
            }
            return input_values[args[0]]

        with patch('prudentia.utils.io.input_value') as iv:
            iv.side_effect = input_side_effect
            self.cli.do_register(None)
            self.assertEqual(self.cli.provider.get_box(expected_box.name), expected_box)

    def test_redefine_box(self):
        expected_box = Box(
            name='ssh-test-box',
            playbook=path.join(self.tests_path, 'uname.yml'),
            hostname='localhost',
            ip='4.3.2.1',
            remote_user='everybody',
            remote_pwd='xxx'
        )

        def input_side_effect(*args, **kwargs):
            input_values = {
                'playbook path': 'uname.yml',
                'box name': expected_box.name,
                'instance address or inventory': '4.3.2.1',
                'remote user': 'everybody',
                'password for the remote user': 'xxx'
            }
            return input_values[args[0]]

        with patch('prudentia.utils.io.input_value') as iv:
            iv.side_effect = input_side_effect
            self.cli.do_reconfigure(expected_box.name)
            self.assertEqual(self.cli.provider.get_box(expected_box.name), expected_box)
