import ansible.constants as C

from domain import Box
from provider_simple import SimpleProvider
from util import input_string


class SshProvider(SimpleProvider):
    def __init__(self):
        super(SshProvider, self).__init__('ssh')

    def register(self):
        try:
            playbook = input_string('playbook path')
            name = self.fetch_box_name(playbook)
            ip = input_string('address of the instance')
            user = input_string('remote user', default_value=C.active_user)
            pwd = input_string('password for the remote user', default_description='ssh key', mandatory=False)

            box = Box(name, playbook, ip, user, pwd)
            self.add_box(box)
            print "\nBox %s added." % box
        except Exception as e:
            print '\nThere was some problem while adding the box: %s\n' % e

    def reconfigure(self, box_name):
        try:
            box = self.remove_box(box_name)

            playbook = input_string('playbook path', previous=box.playbook)
            name = self.fetch_box_name(playbook)
            ip = input_string('address of the instance', previous=box.ip)
            user = input_string('remote user', previous=box.remote_user)
            pwd = input_string('password for the remote user', previous=box.remote_pwd, mandatory=False)

            box = Box(name, playbook, ip, user, pwd)
            self.add_box(box)
            print "\nBox %s reconfigured." % box
        except Exception as e:
            print '\nThere was some problem while reconfiguring the box: %s\n' % e

    def provision(self, box_name, tag):
        for box in self.boxes():
            if box_name in box.name:
                super(SshProvider, self).provision(box, tag)
