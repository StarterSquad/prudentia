import logging

from prudentia.domain import Box
from prudentia.simple import SimpleProvider, SimpleCli
from prudentia.utils.io import input_value, input_path


class LocalCli(SimpleCli):
    def __init__(self):
        SimpleCli.__init__(self)
        self.prompt = '(Prudentia > Local) '
        self.provider = LocalProvider()


class LocalProvider(SimpleProvider):
    NAME = 'local'

    def __init__(self):
        super(LocalProvider, self).__init__(self.NAME)

    @staticmethod
    def _prepare(box):
        box.transport = 'local'
        box.use_prudentia_lib = True
        return box

    def register(self):
        try:
            playbook = input_path('playbook path')
            hostname = self.fetch_box_hosts(playbook)
            name = input_value('box name', self.suggest_name(hostname))

            box = Box(name, playbook, hostname, '127.0.0.1')
            self.add_box(box)
            print "\nBox %s added." % box
        except Exception as ex:
            logging.exception('Box not added.')
            print '\nError: %s\n' % ex

    def reconfigure(self, previous_box):
        try:
            self.remove_box(previous_box)

            playbook = input_path('playbook path', previous_box.playbook)
            hostname = self.fetch_box_hosts(playbook)

            box = Box(previous_box.name, playbook, hostname, '127.0.0.1')
            self.add_box(box)
            print "\nBox %s reconfigured." % box
        except Exception as ex:
            logging.exception('Box not reconfigured.')
            print '\nError: %s\n' % ex

    def provision(self, box, *tags):
        super(LocalProvider, self).provision(LocalProvider._prepare(box), *tags)

    @staticmethod
    def facts(box, regex='*'):
        return SimpleProvider.facts(LocalProvider._prepare(box), regex)
