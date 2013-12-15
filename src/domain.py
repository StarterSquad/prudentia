import json
import os


class Environment(object):
    ENVIRONMENT_FILE_NAME = '.boxes'
    file = None
    boxes = list()

    def __init__(self, path, box_extra_type, name=ENVIRONMENT_FILE_NAME):
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
        self.boxes.append(box)
        self.__save()

    def remove(self, box_name):
        self.boxes = [b for b in self.boxes if b.name != box_name]
        self.__save()

    def __load(self):
        f = None
        try:
            f = open(self.file, 'r')
            json_boxes = json.load(f)
            self.boxes = [Box.from_json(j, self.box_extra_type) for j in json_boxes]
        except IOError, e:
            print e
        finally:
            if f:
                f.close()

    def __save(self):
        json_boxes = [b.to_json() for b in self.boxes]
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
    name = None
    playbook = None
    ip = None
    pwd = None
    extra = None

    def set_name(self, name):
        self.name = name

    def set_playbook(self, pb):
        self.playbook = pb

    def set_ip(self, ip):
        self.ip = ip

    def set_pwd(self, pwd):
        self.pwd = pwd

    def set_extra(self, ex):
        self.extra = ex

    def use_ssh_key(self):
        return self.pwd is None

    def inventory(self):
        return '[' + self.name + ']\n' + self.ip

    def __repr__(self):
        return '%s -> (%s, %s, %s)' % (self.name, self.playbook, self.ip, self.extra)

    def to_json(self):
        return {
            'name': self.name,
            'playbook': self.playbook,
            'ip': self.ip,
            'pwd': self.pwd,
            'extra': self.extra.to_json() if self.extra else None
        }

    @staticmethod
    def from_json(json_value, extra_type):
        b = Box()
        b.set_name(json_value['name'])
        b.set_playbook(json_value['playbook'])
        b.set_ip(json_value['ip'])
        b.set_pwd(json_value['pwd'])
        if extra_type:
            b.set_extra(extra_type.from_json(json_value['extra']))
        return b