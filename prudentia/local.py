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

    def define_box(self):
        playbook = io.input_path('playbook path')
        hostname = self.fetch_box_hosts(playbook)
        name = io.input_value('box name', self.suggest_name(hostname))
        return Box(name, playbook, hostname, '127.0.0.1')

    def redefine_box(self, previous_box):
        playbook = io.input_path('playbook path', previous_box.playbook)
        hostname = self.fetch_box_hosts(playbook)
        return Box(previous_box.name, playbook, hostname, previous_box.ip)

    def provision(self, box, tags):
        super(LocalProvider, self).provision(LocalProvider._prepare(box), tags)

    def facts(self, box, regex='*'):
        return super(LocalProvider, self).facts(LocalProvider._prepare(box), regex)
