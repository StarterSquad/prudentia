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

    DEFAULT_VAGRANT_PWD = 'vagrant'

    box_name_pattern = re.compile('- hosts: (.*)')

    def __init__(self):
        super(VagrantProvider, self).__init__('vagrant', VagrantExt)
        self.template_env = Environment(loader=FileSystemLoader('./src'), auto_reload=True)
        install_vagrant = BashCmd('./bin/install_vagrant.sh')
        install_vagrant.execute()

    def add_box(self):
        playbook = raw_input('Specify the playbook path: ')

        f = name = None
        try:
            f = open(playbook, 'r')
            for i, line in enumerate(f):
                if i == 1: # 2nd line contains the host name
                    match = self.box_name_pattern.match(line)
                    name = match.group(1)
                elif i > 1:
                    break
        except Exception as e:
            print 'There was a problem while reading %s: ' % playbook, e
        finally:
            if f:
                f.close()

        ip = raw_input('Specify an internal IP: ')

        ext = VagrantExt()
        mem = raw_input('Specify amount of RAM in GB [default 1] : ')
        if not len(mem.strip()):
            ext.set_mem(1024)
        else:
            ext.set_mem(int(mem) * 1024)

        shares = []
        loop = True
        while loop:
            ans = raw_input('Do you want to share a folder? [y/N] ')
            if ans.lower() in ('y', 'yes'):
                src = raw_input('-> enter the dir on the host machine: ')
                dst = raw_input('-> enter the dir on the guest machine: ')
                shares.append((src, dst))
            else:
                loop = False
        ext.set_shares(shares)

        if name and playbook and ip:
            box = Box()
            box.set_name(name)
            box.set_playbook(playbook)
            box.set_ip(ip)
            box.set_pwd(self.DEFAULT_VAGRANT_PWD)
            box.set_extra(ext)
            self.env.add(box)
            self.load_tags(box)
            print "\n%s added.\n" % box
            self._generate_vagrant_file()
            self._up(name)
        else:
            print 'There was some problem while adding the box.'

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
#
#    def provision(self, box_name, tags):
#        start = datetime.now()
#        self.action(action="provision", action_args=(box_name,), tags=tags)
#        end = datetime.now()
#        diff = end - start
#        print "Took {0} seconds\n".format(diff.seconds)
#
#    def reload(self, box_name):
#        self.action(action="reload", action_args=("--no-provision", box_name))
#
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

    def set_mem(self, mem):
        self.mem = mem

    def set_shares(self, shares):
        self.shares = shares

    def __repr__(self):
        return 'VagrantExt[mem: %s, shares: %s]' % (self.mem, self.shares)

    def toJson(self):
        return {'mem':self.mem, 'shares':self.shares}

    @staticmethod
    def fromJson(json):
        e = VagrantExt()
        e.set_mem(json['mem'])
        e.set_shares(json['shares'])
        return e
