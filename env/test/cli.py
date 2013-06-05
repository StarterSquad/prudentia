import readline
import rlcompleter
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")

import cmd
import logging
import sys
import traceback
from datetime import datetime
from subprocess import PIPE, Popen
from threading  import Thread
from jinja2 import  Environment, PackageLoader

class CLI(cmd.Cmd):
    BOXES = ['fe_dev', 'fe_be_dev', 'scraper_dev']

    def setup(self):
        self.prompt = '(Cli) '
        self.vagrant = Vagrant()
        # TODO install ansible and vagrant


    def complete_box_names(self, text, line, begidx, endidx):
        if not text:
            completions = self.BOXES[:]
        else:
            completions = [f
                           for f in self.BOXES
                           if f.startswith(text)
            ]
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


    def help_reload(self):
        print "Reload the box\n"

    def complete_reload(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_reload(self, line):
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
    def __init__(self):
        self.template_env = Environment(loader=PackageLoader('cli', '.'), auto_reload=True)

    def configure(self):
        # TODO read those variables from the template
        home = raw_input('Please enter the full path of your home directory: ')
        parent = raw_input('Please enter the full path of the directory where you keep all your GitHub repositories: ')
        ui = parent + '/hubskip-ui'
        search_api = parent + '/search-api'
        hubscraper_worker = parent + '/hubscraper-worker'
        hubscraper_orchestrator = parent + '/hubscraper-orchestrator'
        #
        template = self.template_env.get_template('Vagrantfile.j2')
        template.stream(hubskip_ui_dir=ui,
            search_api_dir=search_api,
            home_dir=home,
            hubscraper_worker_dir=hubscraper_worker,
            hubscraper_orchestrator_dir=hubscraper_orchestrator
        ).dump('Vagrantfile')
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
    cli.cmdloop("\nWelcome to the Deployment Cli!\n")