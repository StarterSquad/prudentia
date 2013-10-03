from collections import namedtuple
from os.path import dirname
import pickle
from datetime import datetime
import os
import re
from ansible.callbacks import DefaultRunnerCallbacks, AggregateStats
from ansible.inventory import Inventory
from ansible.playbook import PlayBook
from ansible.playbook.play import Play
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
    tags = {}

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
            self.load_tags()
        except IOError:
            pass
        finally:
            if f:
                f.close()

    def load_tags(self):
        for b in self.boxes:
            playbook = PlayBook(
                playbook=b.playbook,
                inventory=Inventory([]),
                callbacks=DefaultRunnerCallbacks(),
                runner_callbacks=DefaultRunnerCallbacks(),
                stats=AggregateStats(),
                extra_vars={'prudentia_dir':self.prudentia_root_dir}
            )
            play = Play(playbook, playbook.playbook[0], dirname(b.playbook))
            (matched_tags, unmatched_tags) = play.compare_tags('')
            self.tags.update({b.name: list(unmatched_tags)})

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
        self.load_tags()

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
        output = self.action(action="status", output=False)
        for box in self.boxes:
            pattern = '.*' + box.name + '\s*(.*?) \(virtualbox\).*'
            match = re.match(pattern, output, re.DOTALL)
            status = match.group(1)
            print "%s -> %r\n" % (status, box)

    def provision(self, box_name, tags):
        start = datetime.now()
        self.action(action="provision", action_args=(box_name,), tags=tags)
        end = datetime.now()
        diff = end - start
        print "Took {0} seconds\n".format(diff.seconds)

    def up(self, box_name):
        self.action(action="up", action_args=("--no-provision", box_name))

    def reload(self, box_name):
        self.action(action="reload", action_args=("--no-provision", box_name))

    def halt(self, box_name):
        self.action(action="halt", action_args=(box_name,))

    def destroy(self, box_name):
        self.halt(box_name)
        self.action(action="destroy", action_args=("-f", box_name))

    def action(self, **kwargs):
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
