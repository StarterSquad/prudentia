import readline
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")

import cmd
from vagrant import Vagrant

class CLI(cmd.Cmd):
    def setup(self):
        self.prompt = '(Prudentia) '
        self.vagrant = Vagrant()


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


    def help_phoenix(self):
        print "Destroys and re-provisions the box\n"

    def complete_phoenix(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_phoenix(self, line):
        self.do_destroy(line)
        self.do_provision(line)


    def help_provision(self):
        print "Starts and provisions the box\n"

    def complete_provision(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_provision(self, line):
        self.vagrant.up(line)
        self.vagrant.provision(line, None)


    def help_update(self):
        print "Provisions the box with only updates\n"

    def complete_update(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_update(self, line):
        self.vagrant.provision(line, 'update')


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

    def emptyline(self, *args, **kwargs):
        return ""
