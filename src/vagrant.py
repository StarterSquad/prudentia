import logging
import os

from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader

from domain import Box
from factory import FactoryProvider
from simple import SimpleProvider
from utils.bash import BashCmd
from utils.io import input_string, input_yes_no


class VagrantProvider(FactoryProvider):
    NAME = 'vagrant'
    ENV_DIR = './env/' + NAME
    VAGRANT_FILE_NAME = 'Vagrantfile'
    CONF_FILE = ENV_DIR + '/' + VAGRANT_FILE_NAME

    DEFAULT_VAGRANT_USER = 'vagrant'
    DEFAULT_VAGRANT_PWD = 'vagrant'

    def __init__(self):
        super(VagrantProvider, self).__init__(self.NAME, box_extra_type=VagrantExt)
        self.template_env = Environment(loader=FileSystemLoader('./src'), auto_reload=True)
        install_vagrant = BashCmd('./bin/install_vagrant.sh')
        install_vagrant.execute()

    def register(self):
        try:
            playbook = input_string('playbook path')
            hostname = self.fetch_box_hostname(playbook)
            name = input_string('box name', default_value=self.suggest_name(hostname))
            ip = input_string('internal IP')

            ext = VagrantExt()
            mem = input_string('amount of RAM in GB', default_value=str(1), mandatory=True)
            if mem:
                ext.set_mem(1024)
            else:
                ext.set_mem(int(mem) * 1024)

            ext.set_shares(self._input_shares())

            box = Box(name, playbook, hostname, ip, self.DEFAULT_VAGRANT_USER, self.DEFAULT_VAGRANT_PWD, ext)
            self.add_box(box)
            print "\nBox %s added." % box
        except Exception as e:
            logging.exception('Box not added.')
            print '\nThere was some problem while adding the box: %s\n' % e

    def add_box(self, box):
        SimpleProvider.add_box(self, box)
        self._generate_vagrant_file()
        self.create(box)

    def remove_box(self, box):
        b = super(VagrantProvider, self).remove_box(box)
        self._generate_vagrant_file()
        return b

    def reconfigure(self, previous_box):
        try:
            self.remove_box(previous_box)

            playbook = input_string('playbook path', previous=previous_box.playbook)
            hostname = self.fetch_box_hostname(playbook)
            ip = input_string('internal IP', previous=previous_box.ip)

            ext = VagrantExt()
            mem = input_string('amount of RAM in GB', previous=str(previous_box.extra.mem / 1024), mandatory=True)
            if mem:
                ext.set_mem(1024)
            else:
                ext.set_mem(int(mem) * 1024)

            ext.set_shares(self._input_shares())

            box = Box(previous_box.name, playbook, hostname, ip, self.DEFAULT_VAGRANT_USER, self.DEFAULT_VAGRANT_PWD, ext)
            self.add_box(box)
            print "\nBox %s reconfigured." % box
        except Exception as e:
            logging.exception('Box not reconfigured.')
            print '\nThere was some problem while reconfiguring the box: %s\n' % e

    def _input_shares(self):
        shares = []
        loop = True
        while loop:
            if input_yes_no('share a folder'):
                src = input_string('directory on the HOST machine')
                if not os.path.exists(src):
                    raise ValueError("Directory '%s' on the HOST machine doesn't exists." % src)
                dst = input_string('directory on the GUEST machine')
                shares.append((src, dst))
            else:
                loop = False
        return shares

    def _generate_vagrant_file(self):
        env = self.template_env
        template_name = self.VAGRANT_FILE_NAME + '.j2'
        template = env.get_template(template_name)
        template.stream({
            'boxes': self.boxes()
        }).dump(self.CONF_FILE)

    def create(self, box):
        self.start(box)

    def start(self, box):
        self._action(action="up", action_args=("--no-provision", box.name))

    def stop(self, box):
        self._action(action="halt", action_args=(box.name,))

    def destroy(self, box):
        if input_yes_no('destroy the instance \'{0}\''.format(box.name)):
            self._action(action="destroy", action_args=("-f", box.name))

    #    def status(self):
    #        output = self.action(action="status", output=False)
    #        for box in self.boxes:
    #            pattern = '.*' + box.name + '\s*(.*?) \(virtualbox\).*'
    #            match = re.match(pattern, output, re.DOTALL)
    #            status = match.group(1)
    #            print "%s -> %r\n" % (status, box)

    def _action(self, **kwargs):
        if 'action_args' not in kwargs.keys():
            cmd = BashCmd("vagrant", kwargs['action'])
        else:
            cmd = BashCmd("vagrant", kwargs['action'], *kwargs['action_args'])

        cmd.set_cwd(self.ENV_DIR)
        if 'output' in kwargs.keys():
            cmd.set_show_output(kwargs['output'])
        if 'tags' in kwargs.keys():
            cmd.set_env_var("TAGS", kwargs['tags'])

        # for debugging
        # cmd.set_env_var("VAGRANT_LOG", "INFO")

        cmd.execute()
        if not cmd.is_ok():
            print "ERROR while running: {0}".format(cmd.cmd_args)
        else:
            return cmd.output()


class VagrantExt(object):
    mem = None
    shares = None

    def set_mem(self, mem):
        self.mem = mem

    def set_shares(self, shares):
        self.shares = shares

    def __repr__(self):
        return 'VagrantExt[mem: %s, shares: %s]' % (self.mem, self.shares)

    def to_json(self):
        return {'mem': self.mem, 'shares': self.shares}

    @staticmethod
    def from_json(json):
        e = VagrantExt()
        e.set_mem(json['mem'])
        e.set_shares(json['shares'])
        return e
