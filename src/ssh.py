import logging
import ansible.constants as C

from domain import Box
from simple import SimpleProvider
from util import input_string


class SshProvider(SimpleProvider):
    NAME = 'ssh'

    def __init__(self):
        super(SshProvider, self).__init__(self.NAME)

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
            logging.exception('Box not added.')
            print '\nThere was some problem while adding the box: %s\n' % e

    def reconfigure(self, box):
        try:
            self.remove_box(box)

            playbook = input_string('playbook path', previous=box.playbook)
            name = self.fetch_box_name(playbook)
            ip = input_string('address of the instance', previous=box.ip)
            user = input_string('remote user', previous=box.remote_user)
            pwd = input_string('password for the remote user', previous=box.remote_pwd, mandatory=False)

            box = Box(name, playbook, ip, user, pwd)
            self.add_box(box)
            print "\nBox %s reconfigured." % box
        except Exception as e:
            logging.exception('Box not reconfigured.')
            print '\nThere was some problem while reconfiguring the box: %s\n' % e
