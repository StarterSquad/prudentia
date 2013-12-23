from abc import abstractmethod, ABCMeta

from simple import SimpleCli, SimpleProvider


class FactoryCli(SimpleCli):
    def help_create(self):
        print "Creates the box.\n"

    def complete_create(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_create(self, line):
        self.provider.create(line)


    def help_start(self):
        print "Starts the box.\n"

    def complete_start(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_start(self, line):
        self.provider.start(line)


    def help_restart(self):
        print "Restarts the box.\n"

    def complete_restart(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_restart(self, line):
        self.do_stop(line)
        self.do_start(line)


    def help_phoenix(self):
        print "Regenerates a box: destroy -> create -> provision.\n"

    def complete_phoenix(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_phoenix(self, line):
        self.do_stop(line)
        self.do_destroy(line)
        self.do_create(line)
        self.do_start(line)
        self.do_provision(line)


    def help_stop(self):
        print "Stops the box.\n"

    def complete_stop(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_stop(self, line):
        self.provider.stop(line)


    def help_destroy(self):
        print "Destroys the box.\n"

    def complete_destroy(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_destroy(self, line):
        self.provider.destroy(line)


class FactoryProvider(SimpleProvider):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create(self, box_name):
        pass

    @abstractmethod
    def start(self, box_name):
        pass

    @abstractmethod
    def stop(self, box_name):
        pass

    @abstractmethod
    def destroy(self, box_name):
        pass
