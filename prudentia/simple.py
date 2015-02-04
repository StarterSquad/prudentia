import logging
from os.path import dirname
import re
import os
from abc import ABCMeta, abstractmethod
from cmd import Cmd
import random

from ansible.callbacks import DefaultRunnerCallbacks, AggregateStats
from ansible.inventory import Inventory
from ansible.playbook import PlayBook
from ansible.playbook.play import Play
import ansible.constants as C

from domain import Environment
from utils.provisioning import run_playbook, generate_inventory
from utils.io import prudentia_python_dir


class SimpleCli(Cmd):
    provider = None  # Set by his children

    def cmdloop(self, intro=None):
        try:
            Cmd.cmdloop(self, intro)
        except Exception as e:
            logging.exception('Got a nasty error.')
            print '\nGot a nasty error: %s\n' % e

    def _get_box(self, box_name):
        b = self.provider.env.get(box_name)
        if not b:
            print 'The box \'%s\' you entered does not exists.\n\nAfter typing the command press Tab for box suggestions.\n' % box_name
            return None
        else:
            return b

    def complete_box_names(self, text, line, begidx, endidx):
        completions = ['']
        tokens = line.split(' ')
        action = tokens[0]
        box_name = tokens[1]
        if len(tokens) <= 2:
            # boxes completion
            if not text:
                completions = [b.name for b in self.provider.boxes()]
            else:
                completions = [b.name for b in self.provider.boxes() if b.name.startswith(text)]
        else:
            if action == 'provision':
                # tags completion
                if not text:
                    completions = self.provider.tags[box_name][:]
                else:
                    completions = [t for t in self.provider.tags[box_name] if t.startswith(text)]
                current_tags = tokens[2:]
                completions = [c for c in completions if c not in current_tags]
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
        if box:
            self.provider.reconfigure(box)


    def help_provision(self):
        print "Starts and provisions the box, it accepts as optional argument a playbook tag.\n"

    def complete_provision(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_provision(self, line):
        tokens = line.split(' ')
        box = self._get_box(tokens[0])
        if box:
            self.provider.provision(box, *tokens[1:])


    def help_unregister(self):
        print "Unregisters an existing box.\n"

    def complete_unregister(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_unregister(self, line):
        box = self._get_box(line)
        if box:
            self.provider.unregister(box)


    def help_set(self):
        print "Sets the value of an environment variable. " \
              "During provisioning it will forcibly override the one defined in any playbook.\n"

    def do_set(self, line):
        tokens = line.split(' ')
        variable = tokens[0]
        value = tokens[1]
        self.provider.set_var(variable, value)


    def help_unset(self):
        print "Unsets an existing environment variable.\n"

    def do_unset(self, line):
        self.provider.unset_var(line)


    def help_list(self):
        print "Shows a list of current boxes.\n"

    def do_list(self, line):
        boxes = self.provider.boxes()
        if not len(boxes):
            print 'No box has been registered yet.\n'
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

    box_name_pattern = re.compile('- hosts: (.*)')

    def __init__(self, name, general_type=None, box_extra_type=None):
        self.env = Environment(name, general_type, box_extra_type)
        self.extra_vars = {'prudentia_dir': prudentia_python_dir()}
        self.tags = {}
        self.load_tags()
        self.provisioned = False

    def boxes(self):
        return self.env.boxes.values()

    def set_var(self, var, value):
        self.extra_vars[var] = value
        print "\nSet \'{0}\' -> {1}\n".format(var, value)

    def unset_var(self, var):
        self.extra_vars.pop(var, None)
        print "\nUnset \'{0}\'\n".format(var)

    def add_box(self, box):
        self.env.add(box)
        self.load_tags(box)

    def load_tags(self, box=None):
        for b in ([box] if box else self.boxes()):
            if not os.path.exists(b.playbook):
                print 'WARNING: Box \'{0}\' points to a NON existing playbook. ' \
                      'Please `reconfigure` or `unregister` the box.\n'.format(b.name)
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
        print "\nBox %s removed.\n" % box.name

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

    def provision(self, box, *tags):
        remote_user = C.DEFAULT_REMOTE_USER
        if box.remote_user:
            remote_user = box.remote_user

        remote_pwd = C.DEFAULT_REMOTE_PASS
        transport = C.DEFAULT_TRANSPORT
        if not box.use_ssh_key():
            remote_pwd = box.remote_pwd
            transport = 'paramiko'

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
            only_tags=only_tags
        )
