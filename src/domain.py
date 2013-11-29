import json
import os

class Environment(object):
    ENVIRONMENT_FILE_NAME = '.boxes'
    file = None
    boxes = list()

    def __init__(self, path, name = ENVIRONMENT_FILE_NAME):
        if not os.path.exists(path):
            print "Environment doesn't exists, creating ..."
            os.makedirs(path)
        self.file = path + '/' + name
        try:
            with open(self.file):
                self.__load()
        except IOError:
            print 'No environment file: %s' % self.file


    def add(self, box):
        self.boxes.append(box)
        self.__save()

    def remove(self, box):
        self.boxes = [b for b in self.boxes if b.name != box.name]
        self.__save()

    def __load(self):
        f = None
        try:
            f = open(self.file, 'r')
            jsonBoxes = json.load(f)
            self.boxes = [self.__deserializeBox(b) for b in jsonBoxes]
        except IOError, e:
            print e
        finally:
            if f:
                f.close()

    def __save(self):
        jsonBoxes = [self.__serializeBox(b) for b in self.boxes]
        f = None
        try:
            f = open(self.file, 'w')
            json.dump(jsonBoxes, f)
        except IOError, e:
            print(e)
        finally:
            if f:
                f.close()

    def __serializeBox(self, box):
        return {'name': box.name, 'playbook': box.playbook, 'ip': box.ip, 'extra': box.extra}

    def __deserializeBox(self, json):
        return Box(json['name'], json['playbook'], json['ip'], json['extra'])


class Box(object):
    name = None
    playbook = None
    ip = None
    extra = None

    def __init__(self, name, playbook, ip, extra = None):
        if (name or playbook or ip) is None:
            raise Exception("Missing required box parameter: {0},{1},{2}" % name, playbook, ip)
        self.name = name
        self.playbook = playbook
        self.ip = ip
        self.extra = extra

    def inventory(self):
        return '[' + self.name + ']\n' + self.ip
