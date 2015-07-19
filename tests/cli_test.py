import unittest

from prudentia.cli import CLI


class TestCli(unittest.TestCase):
    def setUp(self):
        self.cli = CLI()

    def _parse_run(self, *args):
        return self.cli.run(self.cli.parse(args))

    def test_run_failing_provision(self):
        self.assertFalse(self._parse_run('local', 'provision whatever-box'))

    def test_run_list(self):
        self.assertFalse(self._parse_run('local', 'list'))
