import logging

import ansible.constants as C

from domain import Box
from simple import SimpleProvider, SimpleCli
from utils.io import input_value


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
            playbook = input_value('playbook path')
            hostname = self.fetch_box_hostname(playbook)
            name = input_value('box name', self.suggest_name(hostname))
            ip = input_value('address of the instance')
            user = input_value('remote user', C.active_user)
            pwd = input_value('password for the remote user', default_description='ssh key', mandatory=False)

            box = Box(name, playbook, hostname, ip, user, pwd)
            self.add_box(box)
            print "\nBox %s added." % box
        except Exception as e:
            logging.exception('Box not added.')
            print '\nThere was some problem while adding the box: %s\n' % e

    def reconfigure(self, previous_box):
        try:
            self.remove_box(previous_box)

            playbook = input_value('playbook path', previous_box.playbook)
            hostname = self.fetch_box_hostname(playbook)
            ip = input_value('address of the instance', previous_box.ip)
            user = input_value('remote user', previous_box.remote_user)
            pwd = input_value('password for the remote user', previous_box.remote_pwd, mandatory=False)

            box = Box(previous_box.name, playbook, hostname, ip, user, pwd)
            self.add_box(box)
            print "\nBox %s reconfigured." % box
        except Exception as e:
            logging.exception('Box not reconfigured.')
            print '\nThere was some problem while reconfiguring the box: %s\n' % e
