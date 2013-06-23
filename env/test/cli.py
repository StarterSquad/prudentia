import readline

if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")

import cmd
import logging
import sys
import traceback
import os
import re
from datetime import datetime
from subprocess import PIPE, Popen
from threading  import Thread
from jinja2 import  Environment, PackageLoader, meta

class CLI(cmd.Cmd):
    def setup(self):
        self.prompt = '(Prudentia) '
        self.vagrant = Vagrant()
        # TODO install ansible and vagrant


    def complete_box_names(self, text, line, begidx, endidx):
        if not text:
            completions = self.vagrant.BOXES[:]
        else:
            completions = [f for f in self.vagrant.BOXES if f.startswith(text)]
        return completions


    def help_configure(self):
        print "Configures environment\n"

    def do_configure(self, line):
        self.vagrant.configure()

    def help_status(self):
        print "Show current boxes status\n"

    def do_status(self, line):
        self.vagrant.status()


    def help_up(self):
        print "Starts the box\n"

    def complete_up(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_up(self, line):
        self.vagrant.up(line)


    def help_provision(self):
        print "Provisions the box\n"

    def complete_provision(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_provision(self, line):
        # TODO provision <box_name> <comma separated tags> (does up if the box is not running)
        start = datetime.now()
        self.vagrant.provision(line)
        end = datetime.now()
        diff = end - start
        print "\nTook {0} seconds\n".format(diff.seconds)


    def help_restart(self):
        print "Reload the box\n"

    def complete_restart(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_restart(self, line):
        # will halt and the up the box
        self.vagrant.reload(line)


    def help_halt(self):
        print "Stops the box\n"

    def complete_halt(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_halt(self, line):
        self.vagrant.halt(line)


    def help_destroy(self):
        print "Destroys the box\n"

    def complete_destroy(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_destroy(self, line):
        self.vagrant.destroy(line)


    def do_EOF(self, line):
        print "\n\nExiting ..."
        return True

    def emptyline(self):
        return ""


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
        self.action("status")

    def provision(self, box_name):
        self.action("provision", box_name)

    def up(self, box_name):
        self.action("up", "--no-provision", box_name)

    def reload(self, box_name):
        self.action("reload", "--no-provision", box_name)

    def halt(self, box_name):
        self.action("halt", box_name)

    def destroy(self, box_name):
        self.halt(box_name)
        self.action("destroy", "-f", box_name)

    def action(self, action, *args):
        cmd = BashCmd("vagrant", action, *args)
        cmd.execute()
        if not cmd.isOk():
            print "ERROR while running: {0}".format(cmd.cmd_args)


class BashCmd:
    def __init__(self, *cmd_args):
        self.cmd_args = cmd_args
        self.output_stdout = []
        self.output_stderr = []
        self.ON_POSIX = 'posix' in sys.builtin_module_names

    def print_output(self, out, err):
        for line in iter(out.readline, b''):
            print line.strip()
            self.output_stdout.append(line)
        for line in iter(err.readline, b''):
            print "ERR - ", line.strip()
            self.output_stderr.append(line)
        out.close()

    def execute(self):
        try:
            p = Popen(args=self.cmd_args, bufsize=1, stdout=PIPE, stderr=PIPE, close_fds=self.ON_POSIX)
            t = Thread(target=self.print_output, args=(p.stdout, p.stderr))
            t.daemon = True # thread dies with the program
            t.start()
            p.wait()
            self.stdout = "".join(self.output_stdout)
            self.stderr = "".join(self.output_stderr)
            self.returncode = p.returncode
        except Exception as e:
            print("ERROR - Problem running {0}: {1}".format(self.cmd_args, e))
            print traceback.format_exc()

    def __repr__(self):
        return "{0}"\
               "\nReturn code: {1}"\
               "\nStd Output: {2}"\
               "\nStd Error: {3}".format(self.cmd_args, self.returncode, self.stdout, self.stderr)

    def isOk(self):
        if not self.returncode:
            return True
        else:
            return False


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s.%(msecs).03d [%(name)s] %(levelname)s: %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO)

    cli = CLI()
    cli.setup()
    cli.cmdloop()