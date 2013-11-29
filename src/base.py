import os
import sys
import readline
from abc import ABCMeta, abstractmethod, abstractproperty
from cmd import Cmd
from ansible import callbacks, utils, errors
from ansible.inventory import Inventory
from ansible.playbook import PlayBook
from domain import Environment

if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")


class BaseCli(Cmd):
    __metaclass__ = ABCMeta

    @abstractproperty
    def provider(self):
        return

    def complete_box_names(self, text, line, begidx, endidx):
        completions = ['']

        tokens = line.split(' ')
        action = tokens[0]
        box_name = tokens[1]
        if len(tokens) <= 2:
            #boxes completion
            if not text:
                completions = self.provider.boxes[:]
            else:
                completions = [f for f in self.provider.boxes if f.startswith(text)]
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

    @abstractmethod
    def do_add_box(self, line):
        return

    def help_provision(self):
        print "Starts and provisions the box, it accepts as optional argument an Ansible tag.\n"

    def complete_provision(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    @abstractmethod
    def do_provision(self, line):
        return

class BaseProvider(object):
    __metaclass__ = ABCMeta

    ENVIRONMENTS_PATH = './env/'
    env = None

    def __init__(self, name, path = ENVIRONMENTS_PATH):
        cwd = os.path.realpath(__file__)
        components = cwd.split(os.sep)
        self.prudentia_root_dir = str.join(os.sep, components[:components.index("prudentia") + 1])
        self.env = Environment(path + name)

    def boxes(self):
        return self.env.boxes

    def provision(self, box):
        inventory = Inventory(list(box.inventory()))

        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        #if options.step:
        #   playbook_cb.step = options.step
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)

        playbook = PlayBook(
            playbook=box.playbook,
            inventory=inventory,
            callbacks=playbook_cb,
            runner_callbacks=runner_cb,
            #callbacks=DefaultRunnerCallbacks(),
            #runner_callbacks=DefaultRunnerCallbacks(),
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

    def loadTags(self, box):
        # list available tags for a playbook
        pass


    @abstractmethod
    def status(self, box):
        return

    @abstractmethod
    def phoenix(self, box):
        return

    @abstractmethod
    def restart(self, box):
        return

    @abstractmethod
    def stop(self, box):
        return

    @abstractmethod
    def destroy(self, box):
        return
