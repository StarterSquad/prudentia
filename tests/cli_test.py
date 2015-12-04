import unittest

from prudentia import cli


class TestCli(unittest.TestCase):
    def _parse_run(self, *args):
        return cli.run(cli.parse(args))

    def test_run_failing_provision(self):
        self.assertFalse(self._parse_run('local', 'provision whatever-box'))

    def test_run_list(self):
        self.assertFalse(self._parse_run('local', 'list'))
