import re
from base import BaseProvider, BaseCli
from domain import Box

class SshCli(BaseCli):
    provider = SshProvider()

    def do_add_box(self, line):
        self.provider.addBox()

    def do_provision(self, line):
        self.provider.provision(line)


class SshProvider(BaseProvider):
    box_name_pattern = re.compile('- hosts: (.*)')

    def __init__(self):
        BaseProvider.__init__(self, 'ssh')

    def addBox(self):
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

        if name and playbook and ip:
            box = Box(name, playbook, ip)
            self.env.add(box)
            print "\n%r added." % (box,)
        else:
            print 'There was some problem while adding the box.'

    def provision(self, boxName):
        for box in self.boxes():
            if box.name is boxName:
                super(SshProvider).provision(box)