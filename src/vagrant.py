from collections import namedtuple
import pickle
from datetime import datetime
import os
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from util import BashCmd

Box = namedtuple('Box', ['name', 'playbook', 'inventory'])

class Vagrant:
    ENV_DIR = './env/test/'

    VAGRANT_FILE_NAME = 'Vagrantfile'
    CONF_FILE = ENV_DIR + VAGRANT_FILE_NAME

    BOXES = []
    BOXES_FILE = ENV_DIR + '.boxes'


    def __init__(self):
        cwd = os.path.realpath(__file__)
        components = cwd.split(os.sep)
        self.prudentia_root_dir = str.join(os.sep, components[:components.index("prudentia") + 1])
        self.template_env = Environment(loader=FileSystemLoader(self.ENV_DIR), auto_reload=True)
        self.find_current_boxes()

    def find_current_boxes(self):
        f = None
        try:
            f = open(self.BOXES_FILE, 'r')
            self.BOXES = pickle.load(f)
        except IOError:
            pass
        finally:
            if f:
                f.close()

        if self.BOXES:
            print "\nBoxes found: %s\n" % [b.name for b in self.BOXES]
        else:
            print "\nNo boxes found, add one using 'add_box'.\n"

    def save_current_boxes(self):
        f = None
        try:
            f = open(self.BOXES_FILE, 'w')
            pickle.dump(self.BOXES, f)
        except IOError:
            pass
        finally:
            if f:
                f.close()

    def add_box(self):
        env = self.template_env
        template_name = self.VAGRANT_FILE_NAME + '.j2'

        vars = []
        for v in Box._fields:
            var_value = raw_input('Please enter the %s: ' % v)
            vars.append(var_value)

        self.BOXES.append(Box._make(vars))
        self.save_current_boxes()

        template = env.get_template(template_name)
        template.stream({
            'boxes': self.BOXES,
            'prudentia_root_dir': self.prudentia_root_dir
        }).dump(self.CONF_FILE)
        print "\nBox added."

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