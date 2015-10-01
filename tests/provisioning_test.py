import unittest
import mock

from prudentia.utils import provisioning


class TestProvisioning(unittest.TestCase):
    @mock.patch('ansible.runner.Runner')
    def test_host_not_contacted(self, runner):
        runner.run.return_value = {'dark': {}, 'contacted': {}}
        (success, result) = provisioning.run_module(runner)
        self.assertEqual(success, False)

    @mock.patch('ansible.runner.Runner')
    def test_host_contacted(self, runner):
        runner.run.return_value = {'dark': {}, 'contacted': {'host': {'provisioning': 'worked'}}}
        (success, result) = provisioning.run_module(runner)
        self.assertEqual(success, True)

    @mock.patch('ansible.runner.Runner')
    def test_host_failed(self, runner):
        runner.run.return_value = {'dark': {}, 'contacted': {'host': {'failed': True, 'msg': 'Fake error'}}}
        (success, result) = provisioning.run_module(runner)
        self.assertEqual(success, False)
