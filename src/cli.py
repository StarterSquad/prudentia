import sys
from cmd import Cmd

from digital_ocean import DigitalOceanCli
from ssh import SshCli
from vagrant import VagrantCli


Environments = {
    'ssh': SshCli,
    'vagrant': VagrantCli,
    'digital-ocean': DigitalOceanCli
}


class CLI(Cmd):
    parent_loop = False
    env_cli = None

    def __init__(self, *args, **kwargs):
        Cmd.__init__(self, *args, **kwargs)
        self.prompt = '(Prudentia) '

    def cmdloop(self, *args, **kwargs):
        self.parent_loop = True
        print '\nTo start: `use` one of the available providers: %s\n' % ', '.join(
            str(p) for p in Environments.keys())
        return Cmd.cmdloop(self, *args, **kwargs)

    def complete_use(self, text, line, begidx, endidx):
        if not text:
            return Environments.keys()
        else:
            return [e for e in Environments.keys() if e.startswith(text)]

    def do_use(self, env):
        if env in Environments.keys():
            self.env_cli = Environments[env]()
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
