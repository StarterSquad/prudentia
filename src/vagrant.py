from collections import namedtuple
import pickle
from datetime import datetime
import os
import re
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from util import BashCmd

Box = namedtuple('Box', ['name', 'playbook', 'ip', 'shares'])
Share = namedtuple('Share', ['src', 'dst'])

class Vagrant:
    ENV_DIR = './env/test/'

    VAGRANT_FILE_NAME = 'Vagrantfile'
    CONF_FILE = ENV_DIR + VAGRANT_FILE_NAME

    BOXES_FILE = ENV_DIR + '.boxes'
    boxes = []

    box_name_pattern = re.compile('- hosts: (.*)')

    def __init__(self):
        cwd = os.path.realpath(__file__)
        components = cwd.split(os.sep)
        self.prudentia_root_dir = str.join(os.sep, components[:components.index("prudentia") + 1])
        self.template_env = Environment(loader=FileSystemLoader(self.ENV_DIR), auto_reload=True)
        self.load_current_boxes()

    def load_current_boxes(self):
        f = None
        try:
            f = open(self.BOXES_FILE, 'r')
            self.boxes = pickle.load(f)
        except IOError:
            pass
        finally:
            if f:
                f.close()

    def save_current_boxes(self):
        f = None
        try:
            f = open(self.BOXES_FILE, 'w')
            pickle.dump(self.boxes, f)
        except IOError:
            pass
        finally:
            if f:
                f.close()
        self.generate_vagrant_file()

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

        shares = []
        loop = True
        while loop:
            ans = raw_input('Do you want to share a folder? [y/N] ')
            if ans.lower() in ('y', 'yes'):
                src = raw_input('-> enter the dir on the host machine: ')
                dst = raw_input('-> enter the dir on the guest machine: ')
                shares.append(Share(src, dst))
            else:
                loop = False

        if name and playbook and ip:
            box = Box(name, playbook, ip, shares)
            self.boxes.append(box)
            self.save_current_boxes()
            print "\n%r added." % (box,)
        else:
            print 'There was some problem while adding the box.'

    def remove_box(self, box_name):
        self.boxes = [b for b in self.boxes if b.name != box_name]
        self.save_current_boxes()
        print "\nBox %s removed." % box_name

    def status(self):
        self.action(None, "status")

    def provision(self, box_name, tags):
        start = datetime.now()
        self.action(tags, "provision", box_name)
        end = datetime.now()
        diff = end - start
        print "Took {0} seconds\n".format(diff.seconds)

    def up(self, box_name):
        self.action(None, "up", "--no-provision", box_name)

    def reload(self, box_name):
        self.action(None, "reload", "--no-provision", box_name)

    def halt(self, box_name):
        self.action(None, "halt", box_name)

    def destroy(self, box_name):
        self.halt(box_name)
        self.action(None, "destroy", "-f", box_name)

    def action(self, tags, action, *args):
        cmd = BashCmd("vagrant", action, *args)
        cmd.set_cwd(self.ENV_DIR)
        # for debugging
        # cmd.set_env_var("VAGRANT_LOG", "INFO")
        if tags:
            cmd.set_env_var("TAGS", tags)
        cmd.execute()
        if not cmd.isOk():
            print "ERROR while running: {0}".format(cmd.cmd_args)
