import unittest

from prudentia.local import LocalCli


class TestLocalCli(unittest.TestCase):
    def setUp(self):
        self.cli = LocalCli()

    def test_set_var(self):
        var_name = 'var_name'
        var_value = 'var_value'
        self.cli.do_set(var_name + ' ' + var_value)
        self.assertEqual(self.cli.provider.extra_vars[var_name], var_value)

    def test_decrypt(self):
        pwd = "this is a pwd"
        self.cli.do_decrypt(pwd)
        self.assertEqual(self.cli.provider.vault_password, pwd)
