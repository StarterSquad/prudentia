import os
from os.path import dirname
import sys
import readline
from abc import ABCMeta
from cmd import Cmd
from ansible import callbacks, utils, errors
from ansible.callbacks import DefaultRunnerCallbacks, AggregateStats
from ansible.inventory import Inventory
from ansible.playbook import PlayBook
from ansible.playbook.play import Play
import ansible.constants as C
from domain import Environment

if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")


class BaseCli(Cmd):
    provider = None # Set by his children

    def complete_box_names(self, text, line, begidx, endidx):
        if not text:
            completions = [b.name for b in self.provider.boxes()]
        else:
            completions = [b.name for b in self.provider.boxes() if b.name.startswith(text)]

#        tokens = line.split(' ')
#        action = tokens[0]
#        box_name = tokens[1]
#        if len(tokens) <= 2:
#            #boxes completion
#            if not text:
#                completions = self.provider.boxes[:]
#            else:
#                completions = [f for f in self.provider.boxes if f.startswith(text)]
#        else:
#            if action == 'provision':
#                #tags completion
#                if not text:
#                    completions = self.tags[box_name][:]
#                else:
#                    completions = [f for f in self.tags[box_name] if f.startswith(text)]
#            else:
#                completions = ['']
        return completions

    def help_add_box(self):
        print "Adds a box.\n"

    def do_add_box(self, line):
        self.provider.add_box()


    def help_provision(self):
        print "Starts and provisions the box, it accepts as optional argument an Ansible tag.\n"

    def complete_provision(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_provision(self, line):
        self.provider.provision(line)


    def help_rm_box(self):
        print "Removes a box.\n"

    def complete_rm_box(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_rm_box(self, line):
        self.provider.remove_box(line)


    def help_status(self):
        print "Show current boxes status.\n"

    def do_status(self, line):
        for b in self.provider.boxes():
            print b


    def help_phoenix(self):
        print "Destroys and re-provisions the box.\n"

    def complete_phoenix(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_phoenix(self, line):
        return


    def help_restart(self):
        print "Reload the box.\n"

    def complete_restart(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_restart(self, line):
        return


    def help_stop(self):
        print "Stops the box.\n"

    def complete_stop(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_stop(self, line):
        return


    def help_destroy(self):
        print "Destroys the box.\n"

    def complete_destroy(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_destroy(self, line):
        return


    def do_EOF(self, line):
        print "\n"
        return True

    def emptyline(self, *args, **kwargs):
        return ""


class BaseProvider(object):
    __metaclass__ = ABCMeta

    DEFAULT_ENVIRONMENTS_PATH = './env/'
    DEFAULT_PRUDENTIA_INVENTORY = '/tmp/prudentia-inventory'
    env = None

    def __init__(self, name, box_extra_type, path = DEFAULT_ENVIRONMENTS_PATH):
        cwd = os.path.realpath(__file__)
        components = cwd.split(os.sep)
        self.prudentia_root_dir = str.join(os.sep, components[:components.index("prudentia") + 1])
        self.env = Environment(path + name, box_extra_type)

    def boxes(self):
        return self.env.boxes

    def add_box(self):
        # children implements it
        return

    def remove_box(self, box_name):
        self.env.remove(box_name)
        print "\nBox %s removed." % box_name

    def provision(self, box):
        self._generate_inventory(box)
        inventory = Inventory(self.DEFAULT_PRUDENTIA_INVENTORY)

        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=True)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)

        remote_pwd = C.DEFAULT_REMOTE_PASS
        transport = C.DEFAULT_TRANSPORT
        if not box.use_ssh_key():
            remote_pwd = box.pwd
            transport = 'paramiko'
        playbook = PlayBook(
            playbook=box.playbook,
            inventory=inventory,
            remote_pass=remote_pwd,
            transport=transport,
            callbacks=playbook_cb,
            runner_callbacks=runner_cb,
            stats=stats,
            extra_vars={'prudentia_dir':self.prudentia_root_dir}
        )

        try:
            playbook.run()

            hosts = sorted(playbook.stats.processed.keys())
            print callbacks.banner("PLAY RECAP")
            playbook_cb.on_stats(playbook.stats)
            for h in hosts:
                t = playbook.stats.summarize(h)
            #print "%-30s : %s %s %s %s " % (
            #   hostcolor(h, t),
            #   colorize('ok', t['ok'], 'green'),
            #   colorize('changed', t['changed'], 'yellow'),
            #   colorize('unreachable', t['unreachable'], 'red'),
            #   colorize('failed', t['failures'], 'red'))

            print "\n"
            for h in hosts:
                stats = playbook.stats.summarize(h)
                if stats['failures'] != 0 or stats['unreachable'] != 0:
                    return 2

        except errors.AnsibleError, e:
            print >>sys.stderr, "ERROR: %s" % e

    def _generate_inventory(self, box):
        f = None
        try:
            f = open(self.DEFAULT_PRUDENTIA_INVENTORY, 'w')
            f.write(box.inventory())
        except IOError, e:
            print e
        finally:
            f.close()

    def _load_tags(self, box):
        # list available tags for a playbook
        self.tags = {}
        for b in self.env.boxes:
            playbook = PlayBook(
                playbook=b.playbook,
                inventory=Inventory([]),
                callbacks=DefaultRunnerCallbacks(),
                runner_callbacks=DefaultRunnerCallbacks(),
                stats=AggregateStats(),
                extra_vars={'prudentia_dir': self.prudentia_root_dir}
            )
            play = Play(playbook, playbook.playbook[0], dirname(b.playbook))
            (matched_tags, unmatched_tags) = play.compare_tags('')
            self.tags.update({b.name: list(unmatched_tags)})

