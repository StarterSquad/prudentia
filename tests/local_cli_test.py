import unittest
import os

from prudentia.local import LocalCli


class TestLocalCli(unittest.TestCase):
    def setUp(self):
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

    def test_load_vars(self):
        vars_file = './vars.yml'
        self.cli.do_vars(vars_file)
        xv = self.cli.provider.extra_vars
        self.assertEqual(xv['first'], 'well')
        self.assertEqual(xv['second'], 'those')
        self.assertEqual(xv['third'], 'are')
        self.assertEqual(xv['forth'], 'variables')

    def test_envset(self):
        var_name = 'ev_n1'
        var_value = 'ev_v1'
        self.cli.do_envset(var_name + ' ' + var_value)
        self.assertEqual(os.environ[var_name], var_value)

    def test_verbose(self):
        from ansible import utils
        self.cli.do_verbose('-1')
        self.assertEquals(utils.VERBOSITY, 0)
        self.cli.do_verbose('5')
        self.assertEquals(utils.VERBOSITY, 0)
        self.cli.do_verbose(' 2 ')
        self.assertEquals(utils.VERBOSITY, 2)
