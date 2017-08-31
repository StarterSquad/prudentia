import os
import unittest

from prudentia.domain import Box
from prudentia.vagrant import VagrantProvider, VagrantExt
from prudentia.simple import SimpleProvider


class TestVagrantProvider(unittest.TestCase):
    def setUp(self):
        self.tests_path = os.path.dirname(os.path.realpath(__file__))
        self.provider = VagrantProvider()

    def test_create_tasks_box(self):
        ext = VagrantExt()
        ext.set_mem(1024)
        ext.set_shares([])
        ext.set_image('img')
        ext.set_provider('provider')

        box = Box('vagrant-testbox', self.tests_path + '/../examples/boxes/tasks.yml', 'tasks-host', '10.10.0.23',
                  VagrantProvider.DEFAULT_USER, VagrantProvider.DEFAULT_PWD, ext)

        # The Vagrant add_box will invoke Vagrant as well, we're only interested in the generated Vagrantfile
        SimpleProvider.add_box(self.provider, box)
        self.provider._generate_vagrant_file()
        self.assertTrue('vm.define' in self._read_vagrant_file())

        SimpleProvider.remove_box(self.provider, box)
        self.provider._generate_vagrant_file()
        self.assertFalse('vm.define' in self._read_vagrant_file())

    def _read_vagrant_file(self):
        with open(VagrantProvider.CONF_FILE, "r") as myfile:
            data = myfile.read().replace('\n', '')
        return data
