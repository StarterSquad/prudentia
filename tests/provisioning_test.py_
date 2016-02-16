import unittest

import ansible
from mock import patch
from prudentia.utils import provisioning

from prudentia.domain import Box


class TestProvisioning(unittest.TestCase):
    def happy_run(self):
        return {'dark': {}, 'contacted': {'host': {'provisioning': 'worked'}}}

    @patch('ansible.runner.Runner')
    def test_host_not_contacted(self, runner):
        runner.run.return_value = {'dark': {}, 'contacted': {}}
        (success, result) = provisioning.run_module(runner)
        self.assertEqual(success, False)

    @patch('ansible.runner.Runner')
    def test_host_contacted(self, runner):
        runner.run.return_value = self.happy_run()
        (success, result) = provisioning.run_module(runner)
        self.assertEqual(success, True)

    @patch('ansible.runner.Runner')
    def test_host_failed(self, runner):
        runner.run.return_value = {'dark': {}, 'contacted': {'host': {'failed': True, 'msg': 'Fake error'}}}
        (success, result) = provisioning.run_module(runner)
        self.assertEqual(success, False)

    @patch.object(ansible.runner.Runner, 'run', happy_run)
    def test_runner_with_correct_pattern(self):
        with patch('ansible.runner.Runner.__init__') as runner_mock:
            runner_mock.return_value = None

            b = Box('box-name', 'uname.yml', 'box-host', '0.0.0.0', 'user')
            provisioning.create_user(b)

            args_list = runner_mock.call_args_list
            self.assertEqual(len(args_list), 6)

            for idx, c in enumerate(args_list):
                args, kwargs = c
                if idx == 0:
                    self.assertEqual('localhost', kwargs.get('pattern'))
                else:
                    self.assertEqual(b.hostname, kwargs.get('pattern'))
