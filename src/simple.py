from os.path import dirname
import re
import os
from abc import ABCMeta, abstractmethod
from cmd import Cmd

from ansible.callbacks import DefaultRunnerCallbacks, AggregateStats
from ansible.inventory import Inventory
from ansible.playbook import PlayBook
from ansible.playbook.play import Play
from ansible.runner import Runner
import ansible.constants as C
import random

from domain import Environment
from util_ansible import run_playbook, run_modules
from util_io import prudentia_python_dir


class SimpleCli(Cmd):
    provider = None  # Set by his children

    def _get_box(self, box_name):
        return self.provider.env.get(box_name)

    def complete_box_names(self, text, line, begidx, endidx):
        tokens = line.split(' ')
        action = tokens[0]
        box_name = tokens[1]
        if len(tokens) <= 2:
            #boxes completion
            if not text:
                completions = [b.name for b in self.provider.boxes()]
            else:
                completions = [b.name for b in self.provider.boxes() if b.name.startswith(text)]
        else:
            if action == 'provision':
                #tags completion
                if not text:
                    completions = self.provider.tags[box_name][:]
                else:
                    completions = [t for t in self.provider.tags[box_name] if t.startswith(text)]
            else:
                completions = ['']
        return completions


    def help_register(self):
        print "Registers a new box.\n"

    def do_register(self, line):
        self.provider.register()


    def help_reconfigure(self):
        print "Reconfigures an existing box.\n"

    def complete_reconfigure(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_reconfigure(self, line):
        box = self._get_box(line)
        self.provider.reconfigure(box)


    def help_provision(self):
        print "Starts and provisions the box, it accepts as optional argument a playbook tag.\n"

    def complete_provision(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_provision(self, line):
        tokens = line.split(' ')
        box = self._get_box(tokens[0])
        tag = tokens[1] if len(tokens) > 1 else None
        self.provider.provision(box, tag)


    def help_unregister(self):
        print "Unregisters an existing box.\n"

    def complete_unregister(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_unregister(self, line):
        box = self._get_box(line)
        self.provider.unregister(box)


    def help_list(self):
        print "Show list of current boxes.\n"

    def do_list(self, line):
        boxes = self.provider.boxes()
        if not len(boxes):
            print 'No box has been configured.\n'
        else:
            for b in boxes:
                print b


    def do_EOF(self, line):
        print "\n"
        return True

    def emptyline(self, *args, **kwargs):
        return ""


class SimpleProvider(object):
    __metaclass__ = ABCMeta

    DEFAULT_ENVIRONMENTS_PATH = './env/'
    DEFAULT_PRUDENTIA_INVENTORY = '/tmp/prudentia-inventory'

    box_name_pattern = re.compile('- hosts: (.*)')

    def __init__(self, name, general_type=None, box_extra_type=None, env_dir=DEFAULT_ENVIRONMENTS_PATH):
        self.env = Environment(env_dir + name, general_type, box_extra_type)
        self.extra_vars = {'prudentia_dir': prudentia_python_dir()}
        self.tags = {}
        self.load_tags()
        self.provisioned = None

    def boxes(self):
        return self.env.boxes.values()

    def add_box(self, box):
        self.env.add(box)
        self.load_tags(box)

    def load_tags(self, box=None):
        for b in ([box] if box else self.boxes()):
            if not os.path.exists(b.playbook):
                print 'Box \'{0}\' points to a not existing playbook. ' \
                      'Please reconfigure it or unregister the box.\n'.format(b.name)
            else:
                playbook = PlayBook(
                    playbook=b.playbook,
                    inventory=Inventory([]),
                    callbacks=DefaultRunnerCallbacks(),
                    runner_callbacks=DefaultRunnerCallbacks(),
                    stats=AggregateStats(),
                    extra_vars=self.extra_vars
                )
                play = Play(playbook, playbook.playbook[0], dirname(b.playbook))
                (matched_tags, unmatched_tags) = play.compare_tags('')
                self.tags[b.name] = list(unmatched_tags)

    def remove_box(self, box):
        if box.name in self.tags:
            self.tags.pop(box.name)
        return self.env.remove(box.name)

    @abstractmethod
    def register(self):
        pass

    @abstractmethod
    def reconfigure(self, box):
        pass

    def unregister(self, box):
        self.remove_box(box)
        print "\nBox %s removed." % box.name

    def fetch_box_hostname(self, playbook):
        with open(playbook, 'r') as f:
            hostname = None
            for i, line in enumerate(f):
                if i == 1:  # 2nd line contains the host box_name
                    match = self.box_name_pattern.match(line)
                    hostname = match.group(1)
                elif i > 1:
                    break
        return hostname

    def suggest_name(self, hostname):
        if hostname not in self.env.boxes:
            return hostname
        else:
            return hostname + '-' + str(random.randint(0, 100))

    def provision(self, box, tag=None):
        remote_user = C.DEFAULT_REMOTE_USER
        if box.remote_user:
            remote_user = box.remote_user

        remote_pwd = C.DEFAULT_REMOTE_PASS
        transport = C.DEFAULT_TRANSPORT
        if not box.use_ssh_key():
            remote_pwd = box.remote_pwd
            transport = 'paramiko'

        only_tags = None
        if tag:
            only_tags = [tag]

        self.provisioned = run_playbook(
            playbook_file=box.playbook,
            inventory=self._generate_inventory(box),
            remote_user=remote_user,
            remote_pass=remote_pwd,
            transport=transport,
            extra_vars=self.extra_vars,
            only_tags=only_tags
        )

    def create_user(self, box):
        user = box.remote_user
        if 'root' not in user:
            # TODO add user_home information to the box
            if 'jenkins' in user:
                user_home = '/var/lib/jenkins'
            else:
                user_home = '/home/' + user
            inventory = self._generate_inventory(box)
            run_modules([
                {
                    'summary': 'Creating group \'{0}\' ...'.format(user),
                    'module': Runner(
                        inventory=inventory,
                        remote_user='root',
                        module_name='group',
                        module_args='name={0} state=present'.format(user))
                },
                {
                    'summary': 'Creating user \'{0}\' ...'.format(user),
                    'module': Runner(
                        inventory=inventory,
                        remote_user='root',
                        module_name='user',
                        module_args='name={0} home={1} state=present shell=/bin/bash generate_ssh_key=yes group={0} groups=sudo'.format(user, user_home)
                    )
                },
                {
                    'summary': 'Copy authorized_keys from root ...',
                    'module': Runner(
                        inventory=inventory,
                        remote_user='root',
                        module_name='command',
                        module_args="cp /root/.ssh/authorized_keys {0}/.ssh/authorized_keys".format(user_home)
                    )
                },
                {
                    'summary': 'Set permission on authorized_keys ...',
                    'module': Runner(
                        inventory=inventory,
                        remote_user='root',
                        module_name='file',
                        module_args="path={0}/.ssh/authorized_keys mode=600 owner={1} group={1}".format(user_home, user)
                    )
                },
                {
                    'summary': 'Ensuring sudoers no pwd prompting ...',
                    'module': Runner(
                        inventory=inventory,
                        remote_user='root',
                        module_name='lineinfile',
                        # TODO Add validate='visudo -cf %s' when upgrading to Ansible 1.4
                        module_args="dest=/etc/sudoers state=present regexp=%sudo line='%sudo ALL=(ALL:ALL) NOPASSWD:ALL'"
                    )
                }
            ])

    def _generate_inventory(self, box):
        f = None
        try:
            f = open(self.DEFAULT_PRUDENTIA_INVENTORY, 'w')
            f.write(box.inventory())
        except IOError, e:
            print e
        finally:
            f.close()
        return Inventory(self.DEFAULT_PRUDENTIA_INVENTORY)
