import abc
import json

class BaseProvider(object):
    __metaclass__ = abc.ABCMeta

    environment = None

    def __init__(self, name):
        # /env/<name> is the base path for the provider
        pass

    def loadEnv(self):
        # locate environment
        pass

    def loadTags(self, box):
        # list available tags for a playbook
        pass

    def addBox(self, playbook, ip):
        # add box into the environment
        pass

    def remBox(self, box):
        self.destroy(box)
        # removes box from the environment
        pass

    def provision(self, box):
        # run ansible with box playbook and box inventory
        return


    @abc.abstractmethod
    def status(self, box):
        return

    @abc.abstractmethod
    def phoenix(self, box):
        return

    @abc.abstractmethod
    def restart(self, box):
        return

    @abc.abstractmethod
    def stop(self, box):
        return

    @abc.abstractmethod
    def destroy(self, box):
        return


class Environment(object):
    ENVIRONMENT_FILE_NAME = '.boxes'
    file = None
    boxes = list()

    def __init__(self, path, name = ENVIRONMENT_FILE_NAME):
        self.file = path + '/' + name
        try:
            with open(self.file):
                self.__load()
        except IOError:
            print 'No environment file'


    def addBox(self, box):
        self.boxes.append(box)
        self.__save()

    def remBox(self, name):
        self.boxes = [b for b in self.boxes if b.name != name]
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

    def __init__(self, name, playbook, ip, extra):
        self.name = name
        self.playbook = playbook
        self.ip = ip
        self.extra = extra

    def inventory(self):
        return '[' + self.name + ']\n' + self.ip