from cmd import Cmd

from base import BaseCli
from ssh import SshProvider
from vagrant import VagrantProvider


class SshCli(BaseCli):
    def __init__(self, *args, **kwargs):
        Cmd.__init__(self, *args, **kwargs)
        self.prompt = '(Prudentia > Ssh) '
        self.provider = SshProvider()


class VagrantCli(BaseCli):
    def __init__(self, *args, **kwargs):
        Cmd.__init__(self, *args, **kwargs)
        self.prompt = '(Prudentia > Vagrant) '
        self.provider = VagrantProvider()


class CLI(Cmd):
    parent_loop = False
    cli = None

    environments = {
        'ssh': SshCli,
        'vagrant': VagrantCli
    }

    def __init__(self, *args, **kwargs):
        Cmd.__init__(self, *args, **kwargs)
        self.prompt = '(Prudentia) '

    def cmdloop(self, *args, **kwargs):
        self.parent_loop = True
        print '\nTo start: `use` one of the available providers: %s\n' % ', '.join(
            str(p) for p in self.environments.keys())
        return Cmd.cmdloop(self, *args, **kwargs)


    def complete_use(self, text, line, begidx, endidx):
        if not text:
            return self.environments.keys()
        else:
            return [e for e in self.environments.keys() if e.startswith(text)]

    def do_use(self, env):
        if env in self.environments.keys():
            self.cli = self.environments[env]()
            self.cli.cmdloop()
        else:
            print 'Provider %s NOT found.' % env
        return not self.parent_loop

    def do_EOF(self, line):
        print "\n\nBye!"
        return True

    def emptyline(self, *args, **kwargs):
        return ""
