import re
from base import BaseProvider
from domain import Box

class SshProvider(BaseProvider):
    box_name_pattern = re.compile('- hosts: (.*)')

    def __init__(self):
        super(SshProvider, self).__init__('ssh')


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

        if name and playbook and ip:
            box = Box(name, playbook, ip)
            self.env.add(box)
            print "\n%r added." % (box,)
        else:
            print 'There was some problem while adding the box.'

    def provision(self, box_name):
        for box in self.boxes():
            if box.name is box_name:
                super(SshProvider).provision(box)