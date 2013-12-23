import re
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from base import BaseProvider
from bash import BashCmd
from domain import Box


class VagrantProvider(BaseProvider):
    ENV_DIR = './env/vagrant/'
    VAGRANT_FILE_NAME = 'Vagrantfile'
    CONF_FILE = ENV_DIR + VAGRANT_FILE_NAME

    DEFAULT_VAGRANT_USER = 'vagrant'
    DEFAULT_VAGRANT_PWD = 'vagrant'

    box_name_pattern = re.compile('- hosts: (.*)')

    def __init__(self):
        super(VagrantProvider, self).__init__('vagrant', VagrantExt)
        self.template_env = Environment(loader=FileSystemLoader('./src'), auto_reload=True)
        install_vagrant = BashCmd('./bin/install_vagrant.sh')
        install_vagrant.execute()

    def add_box(self):
        f = name = None
        try:
            playbook = raw_input('Specify the playbook path: ').strip()

            f = open(playbook, 'r')
            for i, line in enumerate(f):
                if i == 1:  # 2nd line contains the host name
                    match = self.box_name_pattern.match(line)
                    name = match.group(1)
                elif i > 1:
                    break

            for box in self.boxes():
                if box.name == name:
                    raise ValueError("Box '%s' already exists" % name)

            ip = raw_input('Specify an internal IP: ').strip()
            if not len(ip):
                # TODO use regex for ip
                raise ValueError("IP '%s' not valid" % ip)

            ext = VagrantExt()
            mem = raw_input('Specify amount of RAM in GB [default 1] : ').strip()
            if not len(mem):
                ext.set_mem(1024)
            else:
                ext.set_mem(int(mem) * 1024)

            shares = []
            loop = True
            while loop:
                ans = raw_input('Do you want to share a folder? [y/N] ').strip()
                if ans.lower() in ('y', 'yes'):
                    src = raw_input('-> Specify a directory on the HOST machine: ').strip()
                    # TODO check src path exists
                    dst = raw_input('-> Specify a directory on the GUEST machine: ').strip()
                    shares.append((src, dst))
                else:
                    loop = False
            ext.set_shares(shares)

            box = Box(name, playbook, ip, self.DEFAULT_VAGRANT_USER, self.DEFAULT_VAGRANT_PWD, ext)
            self.env.add(box)
            self.load_tags(box)
            self._generate_vagrant_file()
            self._up(name)
            print "\nBox %s added.\n" % box
        except Exception as e:
            print '\nThere was some problem while adding the box: %s\n' % e
        finally:
            if f:
                f.close()

    def reconfigure(self, box_name):
        # TODO
        pass

    def _generate_vagrant_file(self):
        env = self.template_env
        template_name = self.VAGRANT_FILE_NAME + '.j2'
        template = env.get_template(template_name)
        template.stream({
            'boxes': self.boxes()
        }).dump(self.CONF_FILE)

    def provision(self, box_name, tag):
        for box in self.boxes():
            if box_name in box.name:
                super(VagrantProvider, self).provision(box, tag)

    def remove_box(self, box_name):
        super(VagrantProvider, self).remove_box(box_name)
        self._destroy(box_name)
        self._generate_vagrant_file()

    def _up(self, box_name):
        self._action(action="up", action_args=("--no-provision", box_name))

    #    def status(self):
    #        output = self.action(action="status", output=False)
    #        for box in self.boxes:
    #            pattern = '.*' + box.name + '\s*(.*?) \(virtualbox\).*'
    #            match = re.match(pattern, output, re.DOTALL)
    #            status = match.group(1)
    #            print "%s -> %r\n" % (status, box)

    def reload(self, box_name):
        self._action(action="reload", action_args=("--no-provision", box_name))

    def _halt(self, box_name):
        self._action(action="halt", action_args=(box_name,))

    def _destroy(self, box_name):
        self._halt(box_name)
        self._action(action="destroy", action_args=("-f", box_name))

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
        if not cmd.isOk():
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
