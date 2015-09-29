import argparse
import os
from os import path
import sys

from . import __version__


# Setting Ansible config file environment variable as first thing
cwd = path.dirname(path.realpath(__file__))
os.environ['ANSIBLE_CONFIG'] = path.join(cwd, 'ansible.cfg')
os.environ['ANSIBLE_ROLES_PATH'] = path.join(cwd, 'roles') + os.pathsep + '/etc/ansible/roles'
os.environ['ANSIBLE_LOOKUP_PLUGINS'] = path.join(cwd, 'plugins', 'lookup') + os.pathsep + '/usr/share/ansible_plugins/lookup_plugins'
os.environ['ANSIBLE_LIBRARY'] = path.join(cwd, 'modules')

from digital_ocean import DigitalOceanCli
from local import LocalCli
from ssh import SshCli
from vagrant import VagrantCli

Providers = {
    'local': LocalCli,
    'ssh': SshCli,
    'vagrant': VagrantCli,
    'digital-ocean': DigitalOceanCli
}


class CLI(object):
    def parse(self, args=None):
        parser = argparse.ArgumentParser(prog='prudentia', description='A useful Continuous Deployment toolkit.')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
        parser.add_argument('provider', choices=Providers.keys(), help='use one of the available providers')
        parser.add_argument('commands', nargs='*', default='',
                            help='optional quoted list of commands to run with the chosen provider')
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)
        return parser.parse_args(args)

    def run(self, args):
        chosen_cli = Providers[args.provider]()
        if args.commands:
            for c in args.commands:
                print "Executing: '{0}'\n".format(c)
                chosen_cli.onecmd(c)
        else:
            chosen_cli.cmdloop()
        return chosen_cli.provider.provisioned
