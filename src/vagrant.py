import re
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from base import BaseProvider
from domain import Box

class VagrantProvider(BaseProvider):
    ENV_DIR = './env/test/'
    VAGRANT_FILE_NAME = 'Vagrantfile'
    CONF_FILE = ENV_DIR + VAGRANT_FILE_NAME

    box_name_pattern = re.compile('- hosts: (.*)')

    def __init__(self):
        super(VagrantProvider, self).__init__('vagrant')
        self.template_env = Environment(loader=FileSystemLoader(self.ENV_DIR), auto_reload=True)

    def generate_vagrant_file(self):
        env = self.template_env
        template_name = self.VAGRANT_FILE_NAME + '.j2'
        template = env.get_template(template_name)
        template.stream({
            'boxes': self.boxes,
            'prudentia_root_dir': self.prudentia_root_dir
        }).dump(self.CONF_FILE)

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

        mem = raw_input('Specify amount of RAM in GB [default 1] : ')
        if not len(mem.strip()):
            mem = 1024
        else:
            mem = int(mem) * 1024

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

        if name and playbook and ip:
            extra = ExtraBox(mem, shares)
            box = Box(name, playbook, ip, extra)
            self.env.add(box)
            print "\n%r added." % (box,)
        else:
            print 'There was some problem while adding the box.'

        #    def remove_box(self, box):
        #        self.env.remove(box)
        #        print "\nBox %s removed." % box.name
        #
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

    def provision(self, box_name):
        for box in self.boxes():
            if box.name is box_name:
                super(VagrantProvider).provision(box)

#
#
#    def up(self, box_name):
#        self.action(action="up", action_args=("--no-provision", box_name))
#
#    def reload(self, box_name):
#        self.action(action="reload", action_args=("--no-provision", box_name))
#
#    def halt(self, box_name):
#        self.action(action="halt", action_args=(box_name,))
#
#    def destroy(self, box_name):
#        self.halt(box_name)
#        self.action(action="destroy", action_args=("-f", box_name))
#
#    def action(self, **kwargs):
#        if 'action_args' not in kwargs.keys():
#            cmd = BashCmd("vagrant", kwargs['action'])
#        else:
#            cmd = BashCmd("vagrant", kwargs['action'], *kwargs['action_args'])
#
#        cmd.set_cwd(self.ENV_DIR)
#        if 'output' in kwargs.keys():
#            cmd.set_show_output(kwargs['output'])
#        if 'tags' in kwargs.keys():
#            cmd.set_env_var("TAGS", kwargs['tags'])
#
#        # for debugging
#        # cmd.set_env_var("VAGRANT_LOG", "INFO")
#
#        cmd.execute()
#        if not cmd.isOk():
#            print "ERROR while running: {0}".format(cmd.cmd_args)
#        else:
#            return cmd.output()

class ExtraBox(object):
    mem = None
    shares = None

    def __init__(self, mem, shares):
        self.mem = mem
        self.shares = shares
