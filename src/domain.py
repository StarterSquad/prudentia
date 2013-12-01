import json
import os

class Environment(object):
    ENVIRONMENT_FILE_NAME = '.boxes'
    file = None
    boxes = list()

    def __init__(self, path, extra_type, name = ENVIRONMENT_FILE_NAME):
        if not os.path.exists(path):
            print "Environment doesn't exists, creating ..."
            os.makedirs(path)
        self.file = path + '/' + name
        self.extra_type = extra_type
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
            jsonBoxes = json.load(f)
            self.boxes = [Box.fromJson(j, self.extra_type) for j in jsonBoxes]
        except IOError, e:
            print e
        finally:
            if f:
                f.close()

    def __save(self):
        jsonBoxes = [b.toJson() for b in self.boxes]
        f = None
        try:
            f = open(self.file, 'w')
            json.dump(jsonBoxes, f)
        except IOError, e:
            print(e)
        finally:
            if f:
                f.close()


class Box(object):
    def set_name(self, name):
        self.name = name

    def set_playbook(self, pb):
        self.playbook = pb

    def set_ip(self, ip):
        self.ip = ip

    def set_extra(self, ex):
        self.extra = ex

    def inventory(self):
        return '[' + self.name + ']\n' + self.ip

    def __str__(self):
        return 'Box[name: %s, playbook: %s, ip: %s, extra: %s]' % (self.name, self.playbook, self.ip, self.extra)

    def toJson(self):
        return {'name': self.name, 'playbook': self.playbook, 'ip': self.ip, 'extra': self.extra.toJson()}

    @staticmethod
    def fromJson(json, extra_type):
        b = Box()
        b.set_name(json['name'])
        b.set_playbook(json['playbook'])
        b.set_ip(json['ip'])
        b.set_extra(extra_type.fromJson(json['extra']))
        return b