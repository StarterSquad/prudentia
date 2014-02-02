from cmd import Cmd
import sys

from factory import FactoryCli
from simple import SimpleCli
from ssh import SshProvider
from vagrant import VagrantProvider
from digital_ocean import DigitalOceanProvider


class SshCli(SimpleCli):
    def __init__(self, *args, **kwargs):
        Cmd.__init__(self, *args, **kwargs)
        self.prompt = '(Prudentia > Ssh) '
        self.provider = SshProvider()


class VagrantCli(FactoryCli):
    def __init__(self, *args, **kwargs):
        Cmd.__init__(self, *args, **kwargs)
        self.prompt = '(Prudentia > Vagrant) '
        self.provider = VagrantProvider()


class DigitalOceanCli(FactoryCli):
    def __init__(self, *args, **kwargs):
        Cmd.__init__(self, *args, **kwargs)
        self.prompt = '(Prudentia > DigitalOcean) '
        self.provider = DigitalOceanProvider()        


class CLI(Cmd):
    parent_loop = False
    env_cli = None

    environments = {
        'ssh': SshCli,
        'vagrant': VagrantCli,
        'digital-ocean': DigitalOceanCli
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
            self.env_cli = self.environments[env]()
            if len(sys.argv) > 2:
                cmd = ' '.join(sys.argv[2:])
                print "Executing: '{0}'\n".format(cmd)
                self.env_cli.onecmd(cmd)
            else:
                self.env_cli.cmdloop()
        else:
            print "Provider '{0}' NOT found.".format(env)
        return not self.parent_loop

    def do_EOF(self, line):
        print "\n\nBye!"
        return True

    def emptyline(self, *args, **kwargs):
        return ""
