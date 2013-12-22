import re
from base import BaseProvider
from domain import Box


class SshProvider(BaseProvider):
    box_name_pattern = re.compile('- hosts: (.*)')

    def __init__(self):
        super(SshProvider, self).__init__('ssh')

    def add_box(self):
        f = name = None
        try:
            playbook = raw_input('Specify the playbook path: ').strip()

            f = open(playbook, 'r')
            for i, line in enumerate(f):
                if i == 1:  # 2nd line contains the host name
                    match = self.box_name_pattern.match(line)
                    name = match.group(1)
                elif i > 1:
                    break

            for box in self.boxes():
                if box.name == name:
                    raise ValueError("Box '%s' already exists" % name)

            ip = raw_input('Specify the address of the instance: ').strip()
            if not len(ip):
                # TODO use regex for ip and domain
                raise ValueError("Address '%s' not valid" % ip)

            pwd = raw_input('Specify a password [default use ssh key]: ').strip()

            box = Box()
            box.set_name(name)
            box.set_playbook(playbook)
            box.set_ip(ip)
            if len(pwd):
                box.set_pwd(pwd)
            self.env.add(box)
            self.load_tags(box)
            print "\nBox %s added." % box
        except Exception as e:
            print '\nThere was some problem while adding the box: %s\n' % e
        finally:
            if f:
                f.close()

    def provision(self, box_name, tag):
        for box in self.boxes():
            if box_name in box.name:
                super(SshProvider, self).provision(box, tag)
