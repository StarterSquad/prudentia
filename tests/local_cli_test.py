import os
import unittest

from prudentia.local import LocalCli


class TestLocalCli(unittest.TestCase):
    def setUp(self):
        self.tests_path = os.path.dirname(os.path.realpath(__file__))
        self.cli = LocalCli()

    def test_set_var(self):
        var_name = 'var_n1'
        var_value = 'var_v1'
        self.cli.do_set(var_name + ' ' + var_value)
        self.assertEqual(self.cli.provider.extra_vars[var_name], var_value)

    def test_var_with_space(self):
        var_name = 'var_n2'
        var_value = 'var v2 spaced'
        self.cli.do_set(var_name + ' ' + var_value)
        self.assertEqual(self.cli.provider.extra_vars[var_name], var_value)

    def test_override_var(self):
        var_name = 'var_name'
        var_value = 'var_value'
        self.cli.do_set(var_name + ' ' + var_value)
        var_value_overridden = 'over'
        self.cli.do_set(var_name + ' ' + var_value_overridden)
        self.assertEqual(self.cli.provider.extra_vars[var_name], var_value_overridden)

    def test_decrypt(self):
        pwd = "this is a pwd"
        self.cli.do_decrypt(pwd)
        self.assertEqual(self.cli.provider.vault_password, pwd)

    def test_load_vars(self):
        vars_file = self.tests_path + '/vars.yml'
        self.cli.do_vars(vars_file)
        self.assertDictContainsSubset({'third': 'are', 'second': 'those', 'forth': 'variables', 'first': 'well'}, self.cli.provider.extra_vars)
