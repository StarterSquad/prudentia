import json
import os
from os import path
import sys

from utils.io import xstr


class Environment(object):
    DEFAULT_ENVS_PATH = path.join(os.environ['PRUDENTIA_USER_DIR'], 'envs')
    DEFAULT_ENV_FILE_NAME = 'boxes.json'

    def __init__(self, id_env, general_type=None, box_extra_type=None, envs_path=DEFAULT_ENVS_PATH,
                 file_name=DEFAULT_ENV_FILE_NAME):
        self.id_env = id_env
        env_path = path.join(envs_path, id_env)
        if not os.path.exists(env_path):
            print 'Initializing environment {0} ({1}) ...'.format(id_env, env_path)
            os.makedirs(env_path)
        self.file = path.join(env_path, file_name)
        self.general_type = general_type
        self.box_extra_type = box_extra_type
        self.general = None
        self.boxes = {}
        try:
            with open(self.file):
                self._load()
                self.initialized = True
        except IOError:
            self.initialized = False

    def set_general(self, general):
        self.general = general
        self._save()

    def add(self, box):
        if box.name not in self.boxes:
            self.boxes[box.name] = box
            self._save()
        else:
            raise ValueError("Box name must be unique: '{0}' already exists!".format(box.name))

    def get(self, box_name):
        return self.boxes.get(box_name)

    def remove(self, box):
        b = self.boxes.pop(box.name, None)
        self._save()
        return b

    def _load(self):
        f = None
        try:
            f = open(self.file, 'r')
            json_objects = json.load(f)
            if self.general_type:
                self.general = self.general_type.from_json(json_objects[0])
                json_boxes = json_objects[1]
            else:
                json_boxes = json_objects
            for jb in json_boxes:
                b = Box.from_json(jb, self.box_extra_type)
                self.boxes[b.name] = b
        except IOError, e:
            print e
        finally:
            if f:
                f.close()

    def _save(self):
        json_boxes = [b.to_json() for b in self.boxes.values()]
        f = None
        try:
            f = open(self.file, 'w')
            if self.general_type:
                json.dump([self.general.to_json(), json_boxes], f)
            else:
                json.dump(json_boxes, f)
        except IOError, e:
            print e
        finally:
            if f:
                f.close()


class Box(object):
    def __init__(self, name, playbook, hostname, ip, remote_user=None, remote_pwd=None, extra=None, use_prudentia_lib=False):
        self.name = name
        self.playbook = playbook
        self.hostname = hostname
        self.ip = ip
        self.remote_user = remote_user
        self.remote_pwd = remote_pwd
        self.extra = extra
        self.use_prudentia_lib = use_prudentia_lib

    def use_ssh_key(self):
        return self.remote_pwd is None

    def inventory(self):
        prudentia_python_interpreter = ' ansible_python_interpreter=' + sys.executable
        inv = '[' + self.hostname + ']\n' + self.ip
        if self.use_prudentia_lib:
            inv += prudentia_python_interpreter

        if 'local' not in self.hostname and '127.0.0.1' != self.ip and 'localhost' != self.ip:
            inv += '\n\n[localhost]'
            inv += '\nlocalhost ansible_connection=local' + prudentia_python_interpreter

        inv += '\n'
        return inv

    def __repr__(self):
        values = [self.playbook, self.hostname, self.ip, self.remote_user, '*****' if self.remote_pwd else '', xstr(self.extra)]
        return '%s -> (%s)' % (self.name, ', '.join(i for i in values if i and i.strip()))

    def to_json(self):
        json_obj = {
            'name': self.name,
            'playbook': self.playbook,
            'hostname': self.hostname,
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
            json_obj.get('hostname'),
            json_obj.get('ip'),
            json_obj.get('remote_user'),
            json_obj.get('remote_pwd'),
            extra_type.from_json(json_obj.get('extra')) if extra_type else None
        )
