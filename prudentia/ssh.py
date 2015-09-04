import logging

import ansible.constants as C

from domain import Box
from simple import SimpleProvider, SimpleCli
from utils.io import input_value, input_path


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
            playbook = input_path('playbook path')
            hostname = self.fetch_box_hostname(playbook)
            name = input_value('box name', self.suggest_name(hostname))
            ip = input_value('instance address or inventory')
            user = input_value('remote user', C.active_user)
            pwd = input_value('password for the remote user', default_description='ssh key', mandatory=False, hidden=True)

            box = Box(name, playbook, hostname, ip, user, pwd)
            self.add_box(box)
            print "\nBox %s added." % box
        except Exception as e:
            logging.exception('Box not added.')
            print '\nError: %s\n' % e

    def reconfigure(self, previous_box):
        try:
            self.remove_box(previous_box)

            playbook = input_path('playbook path', previous_box.playbook)
            hostname = self.fetch_box_hostname(playbook)
            ip = input_value('instance address or inventory', previous_box.ip)
            user = input_value('remote user', previous_box.remote_user)
            if previous_box.remote_pwd:
                pwd = input_value('password for the remote user', default_value=previous_box.remote_pwd, default_description='*****', mandatory=False, hidden=True)
            else:
                pwd = input_value('password for the remote user', default_description='ssh key', mandatory=False, hidden=True)

            box = Box(previous_box.name, playbook, hostname, ip, user, pwd)
            self.add_box(box)
            print "\nBox %s reconfigured." % box
        except Exception as e:
            logging.exception('Box not reconfigured.')
            print '\nError: %s\n' % e
