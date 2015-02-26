from abc import abstractmethod, ABCMeta

from simple import SimpleCli, SimpleProvider


class FactoryCli(SimpleCli):
    def help_create(self):
        print "Creates the box.\n"

    def complete_create(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_create(self, line):
        box = self._get_box(line)
        if box:
            self.provider.create(box)


    def help_start(self):
        print "Starts the box.\n"

    def complete_start(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_start(self, line):
        box = self._get_box(line)
        if box:
            self.provider.start(box)


    def help_restart(self):
        print "Restarts the box.\n"

    def complete_restart(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_restart(self, line):
        box = self._get_box(line)
        if box:
            self.provider.stop(box)
            self.provider.start(box)


    def help_phoenix(self):
        print "Regenerates a box: destroy -> create -> provision.\n"

    def complete_phoenix(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_phoenix(self, line):
        box = self._get_box(line)
        if box:
            self.provider.rebuild(box)
            self.provider.provision(box)


    def help_stop(self):
        print "Stops the box.\n"

    def complete_stop(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_stop(self, line):
        box = self._get_box(line)
        if box:
            self.provider.stop(box)


    def help_destroy(self):
        print "Destroys the box.\n"

    def complete_destroy(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_destroy(self, line):
        box = self._get_box(line)
        if box:
            self.provider.destroy(box)

    def help_status(self):
        print "Check the status of the box.\n"

    def complete_status(self, text, line, begidx, endidx):
        return self.complete_box_names(text, line, begidx, endidx)

    def do_status(self, line):
        box = self._get_box(line)
        if box:
            self.provider.status(box)


class FactoryProvider(SimpleProvider):
    __metaclass__ = ABCMeta

    def add_box(self, box):
        self.create(box)
        super(FactoryProvider, self).add_box(box)

    @abstractmethod
    def create(self, box):
        pass

    @abstractmethod
    def start(self, box):
        pass

    @abstractmethod
    def stop(self, box):
        pass

    def remove_box(self, box):
        box = super(FactoryProvider, self).remove_box(box)
        self.destroy(box)
        return box

    @abstractmethod
    def destroy(self, box):
        pass

    def rebuild(self, box):
        self.stop(box)
        self.destroy(box)
        self.create(box)
        self.start(box)

    @abstractmethod
    def status(self, box):
        pass
