import readline

if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")

import cmd
from vagrant import Vagrant

class CLI(cmd.Cmd):
    boxes = None
    tags = None

    def setup(self):
        self.prompt = '(Prudentia) '
        self.vagrant = Vagrant()
        self.update_current_boxes()

    def update_current_boxes(self):
        if self.vagrant.boxes:
            self.boxes = [b.name for b in self.vagrant.boxes]
            self.tags = self.vagrant.tags
            print "\nCurrent boxes: %s\n" % ', '.join(self.boxes)
        else:
            print "\nNo boxes found, add one using `add_box`.\n"


    def complete_box_names(self, text, line, begidx, endidx):
        tokens = line.split(' ')
        action = tokens[0]
        box_name = tokens[1]
        if len(tokens) <= 2:
            #boxes completion
            if not text:
                completions = self.boxes[:]
            else:
                completions = [f for f in self.boxes if f.startswith(text)]
        else:
            if action == 'provision':
                #tags completion
                if not text:
                    completions = self.tags[box_name][:]
                else:
                    completions = [f for f in self.tags[box_name] if f.startswith(text)]
            else:
                completions = ['']
        return completions


    def help_add_box(self):
        print "Adds a box.\n"

    def do_add_box(self, line):
        self.vagrant.add_box()
        self.update_current_boxes()


    def help_rm_box(self):
        print "Removes a box.\n"

    def complete_rm_box(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_rm_box(self, line):
        self.do_destroy(line)
        self.vagrant.remove_box(line)
        self.update_current_boxes()


    def help_status(self):
        print "Show current boxes status.\n"

    def do_status(self, line):
        self.vagrant.status()


    def help_phoenix(self):
        print "Destroys and re-provisions the box.\n"

    def complete_phoenix(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_phoenix(self, line):
        self.do_destroy(line)
        self.do_provision(line)


    def help_provision(self):
        print "Starts and provisions the box, it accepts as optional argument an Ansible tag.\n"

    def complete_provision(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_provision(self, line):
        tokens = line.split(' ')
        box_name = tokens[0]
        tag = tokens[1] if len(tokens) > 1 else None
        self.vagrant.up(box_name)
        self.vagrant.provision(box_name, tag)


    def help_restart(self):
        print "Reload the box.\n"

    def complete_restart(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_restart(self, line):
        self.vagrant.halt(line)
        self.vagrant.up(line)


    def help_stop(self):
        print "Stops the box.\n"

    def complete_stop(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_stop(self, line):
        self.vagrant.halt(line)


    def help_destroy(self):
        print "Destroys the box.\n"

    def complete_destroy(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_destroy(self, line):
        self.vagrant.destroy(line)


    def do_EOF(self, line):
        print "\n\nQuitting ..."
        return True

    def emptyline(self, *args, **kwargs):
        return ""
