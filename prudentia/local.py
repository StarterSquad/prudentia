from prudentia.domain import Box
from prudentia.simple import SimpleProvider, SimpleCli
from prudentia.utils import io


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
            playbook = io.input_path('playbook path')
            hostname = self.fetch_box_hosts(playbook)
            name = io.input_value('box name', self.suggest_name(hostname))

            box = Box(name, playbook, hostname, '127.0.0.1')
            self.add_box(box)
            print "\nBox %s added." % box
        except Exception as ex:
            io.track_error('cannot add box', ex)

    def reconfigure(self, previous_box):
        try:
            playbook = io.input_path('playbook path', previous_box.playbook)
            hostname = self.fetch_box_hosts(playbook)

            box = Box(previous_box.name, playbook, hostname, previous_box.ip)
            self.remove_box(previous_box)
            self.add_box(box)
            print "\nBox %s reconfigured." % box
        except Exception as ex:
            io.track_error('cannot reconfigure box', ex)

    def provision(self, box, *tags):
        super(LocalProvider, self).provision(LocalProvider._prepare(box), *tags)

    @staticmethod
    def facts(box, regex='*'):
        return SimpleProvider.facts(LocalProvider._prepare(box), regex)
