import logging
import os
import pwd
import random
from abc import ABCMeta, abstractmethod
from cmd import Cmd

from ansible.parsing.dataloader import DataLoader
from ansible.playbook import Playbook
from prudentia.domain import Environment
from prudentia.utils import io
from prudentia.utils import provisioning


class SimpleCli(Cmd):
    provider = None  # Set by his children

    def cmdloop(self, intro=None):
        try:
            Cmd.cmdloop(self, intro)
        except Exception as ex:
            io.track_error('something bad happened', ex)

    def complete_box_names(self, text, line, begidx, endidx):
        completions = ['']
        tokens = line.split(' ')
        action = tokens[0]
        box_input = tokens[1]
        if len(tokens) <= 2:
            # boxes completion
            # when matching part of a box names returns only the possible endings
            il = len(box_input)
            completions = [text + b.name[il:] for b in self.provider.boxes() if b.name.startswith(box_input)]
        else:
            if action == 'provision':
                # tags completion
                if not text:
                    completions = self.provider.tags[box_input][:]
                else:
                    completions = [t for t in self.provider.tags[box_input] if t.startswith(text)]
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
        box = self.provider.get_box(line)
        if box:
            self.provider.reconfigure(box)

    @staticmethod
    def help_provision():
        print "Starts and provisions the box, it accepts as optional argument a playbook tag.\n"

    def complete_provision(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_provision(self, line):
        tokens = line.split(' ')
        box = self.provider.get_box(tokens[0])
        if box:
            self.provider.provision(box, tokens[1:])

    @staticmethod
    def help_unregister():
        print "Unregisters an existing box.\n"

    def complete_unregister(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_unregister(self, line):
        box = self.provider.get_box(line)
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
        box = self.provider.get_box(tokens[0])
        if box:
            self.provider.facts(box, *tokens[1:])

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
        self.loader = DataLoader()
        self.provisioned = False
        self.tags = {}
        self.extra_vars = {'prudentia_dir': io.prudentia_python_dir()}
        self.load_tags()
        self.active_user = pwd.getpwuid(os.geteuid())[0]

    def boxes(self):
        return self.env.boxes.values()

    def get_box(self, box_name):
        b = self.env.get(box_name)
        if not b:
            print 'The box \'%s\' you entered does not exists.\n\n' \
                  'After typing the command press Tab for box suggestions.\n' % box_name
            return None
        else:
            return b

    def _show_current_vars(self):
        print 'Current set variables:\n%s\n' % '\n'.join(
            [n + ' -> ' + str(v) for n, v in self.extra_vars.iteritems()]
        )

    def set_var(self, var, value):
        if var in self.extra_vars:
            print 'NOTICE: Variable \'{0}\' is already set to this value: \'{1}\' ' \
                  'and it will be overwritten.'.format(var, self.extra_vars[var])
        self.extra_vars[var] = value
        if provisioning.VERBOSITY > 0:
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
        vault_pwd = io.input_value('Ansible vault password', hidden=True)
        self.loader.set_vault_password(vault_pwd)

    def load_vars(self, vars_file):
        if not vars_file:
            vars_file = io.input_path('path of the variables file')
        vars_dict = self.loader.load_from_file(vars_file)
        for key, value in vars_dict.iteritems():
            self.set_var(key, value)

    def add_box(self, box):
        self.env.add(box)
        self.load_tags(box)

    def load_tags(self, box=None):
        for b in [box] if box else self.boxes():
            if not os.path.exists(b.playbook):
                print 'WARNING: Box \'{0}\' points to a NON existing playbook. ' \
                      'Please `reconfigure` or `unregister` the box.\n'.format(b.name)
            else:
                plays = Playbook.load(b.playbook, loader=self.loader).get_plays()
                all_tags = set()
                for p in plays:
                    for block in p.compile():
                        for task in block.block:
                            all_tags.update(task.tags)
                self.tags[b.name] = list(all_tags)

    def remove_box(self, box):
        if box.name in self.tags:
            self.tags.pop(box.name)
        return self.env.remove(box)

    def register(self):
        try:
            box = self.define_box()
            if box:
                self.add_box(box)
                print "\nBox %s added." % box
        except Exception as ex:
            io.track_error('cannot add box', ex)

    @abstractmethod
    def define_box(self):
        pass

    def reconfigure(self, previous_box):
        try:
            box = self.redefine_box(previous_box)
            if box:
                self.remove_box(previous_box)
                self.add_box(box)
                print "\nBox %s reconfigured." % box
        except Exception as ex:
            io.track_error('cannot reconfigure box', ex)

    @abstractmethod
    def redefine_box(self, previous_box):
        pass

    def unregister(self, box):
        self.remove_box(box)
        print "\nBox %s removed.\n" % box.name

    def fetch_box_hosts(self, playbook):
        ds = self.loader.load_from_file(playbook)
        if ds:
            return ds[0]['hosts']  # a playbook is an array of plays we take the first one

    def suggest_name(self, hostname):
        if hostname not in self.env.boxes:
            return hostname
        else:
            return hostname + '-' + str(random.randint(0, 100))

    def provision(self, box, tags):
        only_tags = None
        if len(tags) > 0:
            only_tags = tags

        self.provisioned = provisioning.run_playbook(
            playbook_file=box.playbook,
            inventory_file=provisioning.generate_inventory(box),
            loader=self.loader,
            remote_user=box.get_remote_user(),
            remote_pass=box.get_remote_pwd(),
            transport=box.get_transport(),
            extra_vars=self.extra_vars,
            only_tags=only_tags
        )

    @staticmethod
    def verbose(value):
        if value:
            try:
                iv = int(value)
            except ValueError:
                iv = -1
            if 0 <= iv <= 4:
                provisioning.VERBOSITY = iv
            else:
                print 'Verbosity value \'{0}\' not allowed, should be a number between 0 and 4.'.format(value)
        else:
            print 'Current verbosity: {0}'.format(provisioning.VERBOSITY)

    def facts(self, box, regex='*'):
        return provisioning.gather_facts(box, regex, self.loader)
