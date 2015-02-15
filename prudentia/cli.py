import os
from os import path

# Setting Ansible config file environment variable as first thing
os.environ['ANSIBLE_CONFIG'] = path.join(path.dirname(path.realpath(__file__)), 'ansible.cfg')

from cmd import Cmd

from digital_ocean import DigitalOceanCli
from local import LocalCli
from ssh import SshCli
from vagrant import VagrantCli

Environments = {
    'local': LocalCli,
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

    def do_use(self, env, *args):
        result = False
        if env in Environments.keys():
            self.env_cli = Environments[env]()
            if args:
                cmd = ' '.join(args)
                print "Executing: '{0}'\n".format(cmd)
                self.env_cli.onecmd(cmd)
            else:
                self.env_cli.cmdloop()

            result = self.env_cli.provider.provisioned
        else:
            print "Provider '{0}' NOT found.".format(env)

        # If this function was called inside a cmd loop the return values indicates whether execution will be terminated
        # returning False will cause interpretation to continue.
        # Otherwise the return value is the result of the 'provision' action.
        return False if self.parent_loop else result

    def do_EOF(self, line):
        print "\n\nBye!"
        return True

    def emptyline(self, *args, **kwargs):
        return ""
