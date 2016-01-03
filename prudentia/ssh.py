import ansible.constants as C

from prudentia.domain import Box
from prudentia.simple import SimpleProvider, SimpleCli
from prudentia.utils import io


class SshCli(SimpleCli):
    def __init__(self):
        SimpleCli.__init__(self)
        self.prompt = '(Prudentia > Ssh) '
        self.provider = SshProvider()


class SshProvider(SimpleProvider):
    NAME = 'ssh'

    def __init__(self):
        super(SshProvider, self).__init__(self.NAME)

    def register(self):
        try:
            playbook = io.input_path('playbook path')
            hostname = self.fetch_box_hosts(playbook)
            name = io.input_value('box name', self.suggest_name(hostname))
            ip = io.input_value('instance address or inventory')
            user = io.input_value('remote user', C.active_user)
            pwd = io.input_value(
                'password for the remote user',
                default_description='ssh key',
                mandatory=False,
                hidden=True
            )

            box = Box(name, playbook, hostname, ip, user, pwd)
            self.add_box(box)
            print "\nBox %s added." % box
        except Exception as ex:
            io.track_error('cannot add box', ex)

    def reconfigure(self, previous_box):
        try:
            self.remove_box(previous_box)

            playbook = io.input_path('playbook path', previous_box.playbook)
            hostname = self.fetch_box_hosts(playbook)
            ip = io.input_value('instance address or inventory', previous_box.ip)
            user = io.input_value('remote user', previous_box.remote_user)
            if previous_box.remote_pwd:
                pwd = io.input_value(
                    'password for the remote user',
                    default_value=previous_box.remote_pwd,
                    default_description='*****',
                    mandatory=False,
                    hidden=True
                )
            else:
                pwd = io.input_value(
                    'password for the remote user',
                    default_description='ssh key',
                    mandatory=False,
                    hidden=True
                )

            box = Box(previous_box.name, playbook, hostname, ip, user, pwd)
            self.add_box(box)
            print "\nBox %s reconfigured." % box
        except Exception as ex:
            io.track_error('cannot reconfigure box', ex)
