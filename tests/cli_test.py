import unittest
from prudentia.cli import CLI


class TestCli(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()


    # CmdLoop tests return always False indicating that the execution will not be terminated
    def test_loop_use_wrong_env(self):
        self.cli.parent_loop = True
        self.assertEqual(self.cli.do_use('whatever-env'), False)

    def test_loop_run_failing_provision(self):
        self.cli.parent_loop = True
        self.assertEqual(self.cli.do_use('local', 'provision', 'whatever-box'), False)

    def test_loop_run_list(self):
        self.cli.parent_loop = True
        self.assertEqual(self.cli.do_use('local', 'list'), False)


    # Terminal tests will return the value of provider.provisioned
    def test_terminal_use_wrong_env(self):
        self.cli.parent_loop = False
        self.assertEqual(self.cli.do_use('whatever-env'), False)

    def test_terminal_run_failing_provision(self):
        self.cli.parent_loop = False
        self.assertEqual(self.cli.do_use('local', 'provision', 'whatever-box'), False)

    def test_terminal_run_list(self):
        self.cli.parent_loop = False
        self.assertEqual(self.cli.do_use('local', 'list'), False)
