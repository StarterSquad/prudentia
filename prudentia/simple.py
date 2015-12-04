import json
import logging
from os.path import dirname
import os
from abc import ABCMeta, abstractmethod
from cmd import Cmd
import random

from ansible import utils
from ansible.callbacks import DefaultRunnerCallbacks, AggregateStats
from ansible.inventory import Inventory
from ansible.playbook import PlayBook
from ansible.playbook.play import Play

from prudentia.domain import Environment
from prudentia.utils.provisioning import run_playbook, generate_inventory, gather_facts
from prudentia.utils.io import prudentia_python_dir, input_path, input_value


class SimpleCli(Cmd):
    provider = None  # Set by his children

    def cmdloop(self, intro=None):
        try:
            Cmd.cmdloop(self, intro)
        except Exception as ex:
            logging.exception('Got a nasty error.')
            print '\nGot a nasty error: %s\n' % ex

    def _get_box(self, box_name):
        b = self.provider.env.get(box_name)
        if not b:
            print 'The box \'%s\' you entered does not exists.\n\n' \
                  'After typing the command press Tab for box suggestions.\n' % box_name
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

    @staticmethod
    def help_register():
        print "Registers a new box.\n"

    def do_register(self, line):
        self.provider.register()

    @staticmethod
    def help_reconfigure():
        print "Reconfigures an existing box.\n"

    def complete_reconfigure(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_reconfigure(self, line):
        box = self._get_box(line)
        if box:
            self.provider.reconfigure(box)

    @staticmethod
    def help_provision():
        print "Starts and provisions the box, it accepts as optional argument a playbook tag.\n"

    def complete_provision(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_provision(self, line):
        tokens = line.split(' ')
        box = self._get_box(tokens[0])
        if box:
            self.provider.provision(box, *tokens[1:])

    @staticmethod
    def help_unregister():
        print "Unregisters an existing box.\n"

    def complete_unregister(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_unregister(self, line):
        box = self._get_box(line)
        if box:
            self.provider.unregister(box)

    @staticmethod
    def help_set():
        print "Sets the value of an Ansible extra variable. " \
              "During provisioning it will forcibly override the one defined in any playbook.\n"

    def do_set(self, line):
        try:
            first_space_idx = line.index(' ')
            name = line[:first_space_idx].strip()
            value = line[first_space_idx:].strip()
            self.provider.set_var(name, value)
        except ValueError:
            logging.exception('Error in setting variable for the current provider.')
            print 'Please provide the name of the variable followed by its value.\n'

    @staticmethod
    def help_envset():
        print "Sets the value of an environment variable.\n"

    def do_envset(self, line):
        try:
            first_space_idx = line.index(' ')
            name = line[:first_space_idx].strip()
            value = line[first_space_idx:].strip()
            os.environ[name] = value
        except ValueError:
            logging.exception('Error in setting variable for the current provider.')
            print 'Please provide the name of the variable followed by its value.\n'

    @staticmethod
    def help_unset():
        print "Unsets an existing Ansible extra variable. " \
              "If this action is invoked without parameter it will show " \
              "the current set of variables.\n"

    def do_unset(self, line):
        self.provider.unset_var(line)

    @staticmethod
    def help_list():
        print "Shows a list of current boxes.\n"

    def do_list(self, line):
        boxes = self.provider.boxes()
        if not len(boxes):
            print 'No box has been registered yet.\n'
        else:
            for b in boxes:
                print b

    @staticmethod
    def help_decrypt():
        print "Provides the password that will be used to decrypt Ansible vault files. " \
              "For more information visit http://docs.ansible.com/playbooks_vault.html.\n"

    def do_decrypt(self, line):
        self.provider.set_vault_password()

    @staticmethod
    def help_vars():
        print "Loads Ansible extra vars from a .yml or .json file " \
              "(they will override existing ones).\n"

    def do_vars(self, line):
        self.provider.load_vars(line.strip())

    @staticmethod
    def help_verbose():
        print "Sets Ansible verbosity. Allowed values are " \
              "between 0 (only task status) and 4 (full connection info).\n"

    def do_verbose(self, line):
        self.provider.verbose(line.strip())

    @staticmethod
    def help_facts():
        print 'Gathers and shows useful information about the box. ' \
              'Accepts optional parameter to filter shown properties.'

    def complete_facts(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_facts(self, line):
        tokens = line.split(' ')
        box = self._get_box(tokens[0])
        if box:
            print self.provider.facts(box, *tokens[1:])

    @staticmethod
    def do_EOF(line):
        print "\n"
        return True

    def emptyline(self, *args, **kwargs):
        return ""


class SimpleProvider(object):
    __metaclass__ = ABCMeta

    def __init__(self, name, general_type=None, box_extra_type=None):
        self.env = Environment(name, general_type, box_extra_type)
        self.vault_password = False
        self.provisioned = False
        self.tags = {}
        self.extra_vars = {'prudentia_dir': prudentia_python_dir()}
        self.load_tags()

    def boxes(self):
        return self.env.boxes.values()

    def _show_current_vars(self):
        print 'Current set variables:\n%s\n' % '\n'.join(
            [n + ' -> ' + str(v) for n, v in self.extra_vars.iteritems()]
        )

    def set_var(self, var, value, verbose=True):
        if var in self.extra_vars:
            print 'NOTICE: Variable \'{0}\' is already set to this value: \'{1}\' ' \
                  'and it will be overwritten.'.format(var, self.extra_vars[var])
        self.extra_vars[var] = value
        if verbose:
            print "Set \'{0}\' -> {1}\n".format(var, value)

    def unset_var(self, var):
        if not var:
            print 'Please provide a valid variable name to unset.\n'
            self._show_current_vars()
        elif var not in self.extra_vars:
            print 'WARNING: Variable \'{0}\' is NOT present so cannot be unset.\n'.format(var)
            self._show_current_vars()
        else:
            self.extra_vars.pop(var, None)
            print "Unset \'{0}\'\n".format(var)

    def set_vault_password(self):
        pwd = input_value('Ansible vault password', hidden=True)
        self.vault_password = pwd

    def load_vars(self, vars_file, verbose=True):
        if not vars_file:
            vars_file = input_path('path of the variables file')
        vars_dict = utils.parse_yaml_from_file(vars_file, self.vault_password)
        for key, value in vars_dict.iteritems():
            self.set_var(key, value, verbose)

    def add_box(self, box):
        self.env.add(box)
        self.load_tags(box)

    def _play_from_file(self, playbook_file):
        playbook = PlayBook(
            playbook=playbook_file,
            inventory=Inventory([]),
            callbacks=DefaultRunnerCallbacks(),
            runner_callbacks=DefaultRunnerCallbacks(),
            stats=AggregateStats(),
            extra_vars=self.extra_vars
        )
        return Play(playbook, playbook.playbook[0], dirname(playbook_file))

    def load_tags(self, box=None):
        for b in [box] if box else self.boxes():
            if not os.path.exists(b.playbook):
                print 'WARNING: Box \'{0}\' points to a NON existing playbook. ' \
                      'Please `reconfigure` or `unregister` the box.\n'.format(b.name)
            else:
                play = self._play_from_file(b.playbook)
                (matched_tags, unmatched_tags) = play.compare_tags('')
                self.tags[b.name] = list(unmatched_tags)

    def remove_box(self, box):
        if box.name in self.tags:
            self.tags.pop(box.name)
        return self.env.remove(box)

    @abstractmethod
    def register(self):
        pass

    @abstractmethod
    def reconfigure(self, box):
        pass

    def unregister(self, box):
        self.remove_box(box)
        print "\nBox %s removed.\n" % box.name

    def fetch_box_hosts(self, playbook):
        return self._play_from_file(playbook).hosts

    def suggest_name(self, hostname):
        if hostname not in self.env.boxes:
            return hostname
        else:
            return hostname + '-' + str(random.randint(0, 100))

    def provision(self, box, *tags):
        only_tags = None
        if tags is not ():
            only_tags = tags

        self.provisioned = run_playbook(
            playbook_file=box.playbook,
            inventory=generate_inventory(box),
            remote_user=box.get_remote_user(),
            remote_pass=box.get_remote_pwd(),
            transport=box.get_transport(),
            extra_vars=self.extra_vars,
            only_tags=only_tags,
            vault_password=self.vault_password
        )

    @staticmethod
    def verbose(value):
        iv = int(value)
        if 0 <= iv <= 4:
            utils.VERBOSITY = iv
        else:
            print 'Verbosity value {0} not allowed.'.format(value)

    @staticmethod
    def facts(box, regex='*'):
        (success, result) = gather_facts(box, regex)
        facts_string = ''
        if success:
            res = result['ansible_facts']
            facts_string = json.dumps(res, sort_keys=True, indent=4, separators=(',', ': '))
        return facts_string
