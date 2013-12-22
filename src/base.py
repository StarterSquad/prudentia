import os
from os.path import dirname
import sys
import readline
from abc import ABCMeta, abstractmethod
from cmd import Cmd
from datetime import datetime
from ansible import callbacks, errors
from ansible.callbacks import DefaultRunnerCallbacks, AggregateStats
from ansible.color import stringc
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
    provider = None  # Set by his children

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

    def help_add_box(self):
        print "Adds a box.\n"

    def do_add_box(self, line):
        self.provider.add_box()


    def help_provision(self):
        print "Starts and provisions the box, it accepts as optional argument an Ansible tag.\n"

    def complete_provision(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_provision(self, line):
        tokens = line.split(' ')
        box_name = tokens[0]
        tag = tokens[1] if len(tokens) > 1 else None
        self.provider.provision(box_name, tag)


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

    ## For Factory Providers

    def help_reload(self):
        print "Reload the box.\n"

    def complete_reload(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_reload(self, line):
        self.provider.reload(line)


    def help_phoenix(self):
        print "Destroys and re-provisions the box.\n"

    def complete_phoenix(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_phoenix(self, line):
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

    tags = {}

    def __init__(self, name, box_extra_type=None, path=DEFAULT_ENVIRONMENTS_PATH):
        cwd = os.path.realpath(__file__)
        components = cwd.split(os.sep)
        self.extra_vars = {'prudentia_dir': str.join(os.sep, components[:components.index("prudentia") + 1])}
        self.env = Environment(path + name, box_extra_type)
        self.load_tags()

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
            self.tags.update({b.name: list(unmatched_tags)})

    def boxes(self):
        return self.env.boxes

    @abstractmethod
    def add_box(self):
        pass

    def remove_box(self, box_name):
        self.env.remove(box_name)
        print "\nBox %s removed." % box_name

    def provision(self, box, tag):
        #TODO inventory can be returned from generate and give it to playbook w/o intermediaries
        self._generate_inventory(box)
        inventory = Inventory(self.DEFAULT_PRUDENTIA_INVENTORY)

        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=True)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=True)

        remote_pwd = C.DEFAULT_REMOTE_PASS
        transport = C.DEFAULT_TRANSPORT
        if not box.use_ssh_key():
            remote_pwd = box.pwd
            transport = 'paramiko'
        only_tags = None
        if tag:
            only_tags = [tag]
        playbook = PlayBook(
            playbook=box.playbook,
            inventory=inventory,
            remote_pass=remote_pwd,
            transport=transport,
            callbacks=playbook_cb,
            runner_callbacks=runner_cb,
            stats=stats,
            extra_vars=self.extra_vars,
            only_tags=only_tags
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

            print "Provisioning took {0} minutes\n".format((datetime.now() - start).seconds / 60)
        except errors.AnsibleError, e:
            print >>sys.stderr, "ERROR: %s" % e


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

    def _generate_inventory(self, box):
        f = None
        try:
            f = open(self.DEFAULT_PRUDENTIA_INVENTORY, 'w')
            f.write(box.inventory())
        except IOError, e:
            print e
        finally:
            f.close()
