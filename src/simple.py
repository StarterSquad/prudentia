from os.path import dirname
import sys
import re
from abc import ABCMeta, abstractmethod
from cmd import Cmd
from datetime import datetime

from ansible import callbacks, errors
from ansible.callbacks import DefaultRunnerCallbacks, AggregateStats
from ansible.color import stringc
from ansible.inventory import Inventory
from ansible.playbook import PlayBook
from ansible.playbook.play import Play
from ansible.runner import Runner
import ansible.constants as C

from domain import Environment
from util import prudentia_python_dir


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

    def boxes(self):
        return self.env.boxes.values()

    def add_box(self, box):
        self.env.add(box)
        self.load_tags(box)

    def load_tags(self, box=None):
        for b in ([box] if box else self.boxes()):
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

    def fetch_box_name(self, playbook):
        with open(playbook, 'r') as f:
            box_name = None
            for i, line in enumerate(f):
                if i == 1:  # 2nd line contains the host box_name
                    match = self.box_name_pattern.match(line)
                    box_name = match.group(1)
                elif i > 1:
                    break

        return box_name

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

        self.run_playbook(
            playbook_file=box.playbook,
            inventory=self._generate_inventory(box),
            remote_user=remote_user,
            remote_pass=remote_pwd,
            transport=transport,
            extra_vars=self.extra_vars,
            only_tags=only_tags
        )

    def run_playbook(self, playbook_file, inventory, remote_user=C.DEFAULT_REMOTE_USER,
                     remote_pass=C.DEFAULT_REMOTE_PASS, transport=C.DEFAULT_TRANSPORT, extra_vars=None, only_tags=None):
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=True)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=True)
        playbook = PlayBook(
            playbook=playbook_file,
            inventory=inventory,
            remote_user=remote_user,
            remote_pass=remote_pass,
            transport=transport,
            extra_vars=extra_vars,
            only_tags=only_tags,
            callbacks=playbook_cb,
            runner_callbacks=runner_cb,
            stats=stats
        )

        try:
            start = datetime.now()
            playbook.run()

            hosts = sorted(playbook.stats.processed.keys())
            print callbacks.banner("PLAY RECAP")
            playbook_cb.on_stats(playbook.stats)
            for h in hosts:
                t = playbook.stats.summarize(h)
                print "%s : %s %s %s %s\n" % (
                    self._hostcolor(h, t),
                    self._colorize('ok', t['ok'], 'green'),
                    self._colorize('changed', t['changed'], 'yellow'),
                    self._colorize('unreachable', t['unreachable'], 'red'),
                    self._colorize('failed', t['failures'], 'red'))

            print "Play run took {0} minutes\n".format((datetime.now() - start).seconds / 60)
        except errors.AnsibleError, e:
            print >> sys.stderr, "ERROR: %s" % e

    def create_user(self, box):
        user = box.remote_user
        if 'root' not in user:
            inventory = self._generate_inventory(box)
            print 'Creating group \'{0}\' ...'.format(user)
            self.ansible_run_and_check(Runner(
                inventory=inventory,
                remote_user='root',
                module_name='group',
                module_args='name={0} state=present'.format(user)
            ))
            print 'Creating user \'{0}\' ...'.format(user)
            self.ansible_run_and_check(Runner(
                inventory=inventory,
                remote_user='root',
                module_name='user',
                module_args='name={0} state=present shell=/bin/bash generate_ssh_key=yes group={0} groups=sudo'.format(user)
            ))
            print 'Copy authorized_keys from root ...'
            self.ansible_run_and_check(Runner(
                inventory=inventory,
                remote_user='root',
                module_args="cp /root/.ssh/authorized_keys /home/{0}/.ssh/authorized_keys".format(user)
            ))
            print 'Set permission on authorized_keys ...'
            self.ansible_run_and_check(Runner(
                inventory=inventory,
                remote_user='root',
                module_name='file',
                module_args="path=/home/{0}/.ssh/authorized_keys mode=600 owner={0} group={0}".format(user)
            ))
            print 'Ensuring sudoers no pwd prompting ...'
            self.ansible_run_and_check(Runner(
                inventory=inventory,
                remote_user='root',
                module_name='lineinfile',
                # TODO Add validate='visudo -cf %s' when upgrading to Ansible 1.4
                module_args="dest=/etc/sudoers state=present regexp=%sudo line='%sudo ALL=(ALL:ALL) NOPASSWD:ALL'"
            ))

    def ansible_run_and_check(self, runner):
        results = runner.run()
        for (hostname, result) in results['contacted'].items():
            if 'failed' in result:
                print 'failed: %s' % result['msg']
                return False

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

    def _colorize(self, lead, num, color):
        """ Print 'lead' = 'num' in 'color' """
        if num != 0 and color is not None:
            return "%s%s%-15s" % (stringc(lead, color), stringc("=", color), stringc(str(num), color))
        else:
            return "%s=%-4s" % (lead, str(num))

    def _hostcolor(self, host, stats, color=True):
        if color:
            if stats['failures'] != 0 or stats['unreachable'] != 0:
                return "%-37s" % stringc(host, 'red')
            elif stats['changed'] != 0:
                return "%-37s" % stringc(host, 'yellow')
            else:
                return "%-37s" % stringc(host, 'green')
        return "%-26s" % host
