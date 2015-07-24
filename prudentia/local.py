import logging

import ansible.constants as C
from domain import Box
from simple import SimpleProvider, SimpleCli
from utils.io import input_value, input_path
from utils.provisioning import run_playbook, generate_inventory


class LocalCli(SimpleCli):
    def __init__(self):
        SimpleCli.__init__(self)
        self.prompt = '(Prudentia > Local) '
        self.provider = LocalProvider()


class LocalProvider(SimpleProvider):
    NAME = 'local'

    def __init__(self):
        super(LocalProvider, self).__init__(self.NAME)

    def register(self):
        try:
            playbook = input_path('playbook path')
            hostname = self.fetch_box_hostname(playbook)
            name = input_value('box name', self.suggest_name(hostname))

            box = Box(name, playbook, hostname, '127.0.0.1')
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

            box = Box(previous_box.name, playbook, hostname, '127.0.0.1')
            self.add_box(box)
            print "\nBox %s reconfigured." % box
        except Exception as e:
            logging.exception('Box not reconfigured.')
            print '\nError: %s\n' % e

    def provision(self, box, *tags):
        remote_user = C.DEFAULT_REMOTE_USER
        if box.remote_user:
            remote_user = box.remote_user

        remote_pwd = C.DEFAULT_REMOTE_PASS
        if not box.use_ssh_key():
            remote_pwd = box.remote_pwd

        transport = 'local'
        box.use_prudentia_lib = True

        only_tags = None
        if tags is not ():
            only_tags = tags

        self.provisioned = run_playbook(
            playbook_file=box.playbook,
            inventory=generate_inventory(box),
            remote_user=remote_user,
            remote_pass=remote_pwd,
            transport=transport,
            extra_vars=self.extra_vars,
            only_tags=only_tags,
            vault_password=self.vault_password
        )
