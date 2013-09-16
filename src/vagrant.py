from datetime import datetime
import os
import re
from jinja2 import meta
from jinja2.environment import Environment
from jinja2.loaders import PackageLoader
from util import BashCmd

class Vagrant:
    CONF_FILE = 'Vagrantfile'

    def __init__(self):
        self.template_env = Environment(loader=PackageLoader('cli', '.'), auto_reload=True)
        if not os.path.isfile(self.CONF_FILE):
            print "\nPlease run 'configure' to create a valid %s\n" % self.CONF_FILE
        else:
            self.BOXES = self.find_current_boxes()

    def find_current_boxes(self):
        f = open(self.CONF_FILE, 'r')
        text = f.read()
        f.close()
        pattern = re.compile("config\.vm\.define :(.*) do")

        boxes = []
        for match in pattern.finditer(text):
            boxes.append(match.group(1))

        print "\nBoxes found: %s\n" % boxes
        return boxes

    def configure(self):
        # TODO should use partials to configure multiple boxes
        # TODO the ip in the hosts file should match the private_network ip
        env = self.template_env
        template_name = self.CONF_FILE + '.j2'

        template_source = env.loader.get_source(env, template_name)[0]
        parsed_content = env.parse(template_source)
        undeclared_variables = meta.find_undeclared_variables(parsed_content)

        declared_variables = {}
        for v in undeclared_variables:
            if 'prudentia_root_dir' in v:
                #find the root dir of prudentia
                cwd = os.path.realpath(__file__)
                components = cwd.split(os.sep)
                prudentia_root_dir = str.join(os.sep, components[:components.index("prudentia") + 1])
                declared_variables[v] = prudentia_root_dir
            else:
                var_value = raw_input('Please specify the %s: ' % v)
                declared_variables[v] = var_value
                if 'box_name' in v:
                    # TODO for now only one box is supported
                    self.BOXES = [var_value]

        template = env.get_template(template_name)
        template.stream(declared_variables).dump('Vagrantfile')
        print "\nVagrantfile created."

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
        # for debugging
        # cmd.set_env_var("VAGRANT_LOG", "INFO")
        if tags:
            cmd.set_env_var("TAGS", tags)
        cmd.execute()
        if not cmd.isOk():
            print "ERROR while running: {0}".format(cmd.cmd_args)