import json
import os

from util import xstr


class Environment(object):
    ENVIRONMENT_FILE_NAME = '.boxes'

    file = None
    boxes = {}

    def __init__(self, path, box_extra_type=None, name=ENVIRONMENT_FILE_NAME):
        if not os.path.exists(path):
            print "Environment doesn't exists, creating ..."
            os.makedirs(path)
        self.file = path + '/' + name
        self.box_extra_type = box_extra_type
        try:
            with open(self.file):
                self.__load()
        except IOError:
            print 'No environment file: %s' % self.file

    def add(self, box):
        if box.name not in self.boxes:
            self.boxes[box.name] = box
            self.__save()
        else:
            raise ValueError("Box '%s' already exists." % box.name)

    def get(self, box_name):
        return self.boxes.get(box_name, None)

    def remove(self, box_name):
        b = self.boxes.pop(box_name, None)
        self.__save()
        return b

    def __load(self):
        f = None
        try:
            f = open(self.file, 'r')
            json_boxes = json.load(f)
            for jb in json_boxes:
                b = Box.from_json(jb, self.box_extra_type)
                self.boxes[b.name] = b
        except IOError, e:
            print e
        finally:
            if f:
                f.close()

    def __save(self):
        json_boxes = [b.to_json() for b in self.boxes.values()]
        f = None
        try:
            f = open(self.file, 'w')
            json.dump(json_boxes, f)
        except IOError, e:
            print(e)
        finally:
            if f:
                f.close()


class Box(object):
    def __init__(self, name, playbook, ip, remote_user=None, remote_pwd=None, extra=None):
        self.name = name
        self.playbook = playbook
        self.ip = ip
        self.remote_user = remote_user
        self.remote_pwd = remote_pwd
        self.extra = extra

    def use_ssh_key(self):
        return self.remote_pwd is None

    def inventory(self):
        return '[' + self.name + ']\n' + self.ip

    def __repr__(self):
        values = [self.playbook, self.ip, self.remote_user, '*****' if self.remote_pwd else '', xstr(self.extra)]
        return '%s -> (%s)' % (self.name, ', '.join(i for i in values if i and i.strip()))

    def to_json(self):
        json_obj = {
            'name': self.name,
            'playbook': self.playbook,
            'ip': self.ip
        }
        if self.remote_user:
            json_obj.update({'remote_user': self.remote_user})
        if self.remote_pwd:
            json_obj.update({'remote_pwd': self.remote_pwd})
        if self.extra:
            json_obj.update({'extra': self.extra.to_json()})
        return json_obj

    @staticmethod
    def from_json(json_obj, extra_type):
        return Box(
            json_obj.get('name'),
            json_obj.get('playbook'),
            json_obj.get('ip'),
            json_obj.get('remote_user'),
            json_obj.get('remote_pwd'),
            extra_type.from_json(json_obj.get('extra')) if extra_type else None
        )
