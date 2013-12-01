from cmd import Cmd
from base import BaseCli
from ssh import SshProvider
from vagrant import VagrantProvider

class CLI(Cmd):
    cli = None

    environments = ['ssh', 'vagrant']

    def setup(self):
        self.prompt = '(Prudentia) '

        # TODO temporary
        self.do_use('ssh')

    def complete_use(self, text, line, begidx, endidx):
        if not text:
            return self.environments
        else:
            return [e for e in self.environments if e.startswith(text)]

    def do_use(self, env):
        if 'ssh' in env:
            self.cli = SshCli()
            self.cli.prompt = '(Prudentia > ssh) '
        elif 'vagrant' in env:
            self.cli = VagrantCli()
            self.cli.prompt = '(Prudentia > vagrant) '
        else:
            print 'No provider for environment: %s' % env
            return False
        self.cli.cmdloop()

    def do_EOF(self, line):
        print "\n\nBye!"
        return True

    def emptyline(self, *args, **kwargs):
        return ""

class SshCli(BaseCli):
    provider = SshProvider()

    def do_add_box(self, line):
        self.provider.add_box()

    def do_provision(self, line):
        self.provider.provision(line)

    def do_rm_box(self, line):
        self.provider.remove_box(line)

class VagrantCli(BaseCli):
    provider = VagrantProvider()

    def do_add_box(self, line):
        self.provider.add_box()

    def do_provision(self, line):
        self.provider.provision(line)

    def do_rm_box(self, line):
        self.provider.remove_box(line)
