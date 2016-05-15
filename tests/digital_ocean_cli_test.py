import unittest

from mock import patch, Mock
from prudentia.digital_ocean import DigitalOceanCli, DigitalOceanProvider
from prudentia.domain import Box


class TestDigitalOceanCli(unittest.TestCase):
    mockedProvider = Mock(DigitalOceanProvider)

    def setUp(self):
        def input_side_effect(*args):
            input_values = {'api token': 'yo'}
            return input_values[args[0]]

        with patch('prudentia.utils.io.input_value') as iv:
            iv.side_effect = input_side_effect
            self.cli = DigitalOceanCli()
            self.cli.provider = self.mockedProvider

    def test_phoenix_tags_are_propagated(self):
        expected_box_name = 'do-box'
        expected_box = Box(expected_box_name, './uname.yml', 'localbox-host', '127.0.0.1')
        self.mockedProvider.get_box.return_value = expected_box

        self.cli.do_phoenix('%s tag1 tag2' % expected_box_name)

        self.mockedProvider.rebuild.assert_called_with(expected_box)
        self.mockedProvider.provision.assert_called_with(expected_box, ['tag1', 'tag2'])
