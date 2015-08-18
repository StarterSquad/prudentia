import logging
from os import path
import re

import jinja2
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from domain import Box
from domain import Environment as PrudentiaEnv
from factory import FactoryProvider, FactoryCli
from simple import SimpleProvider
from utils.bash import BashCmd
from utils import io


class VagrantCli(FactoryCli):
    def __init__(self):
        FactoryCli.__init__(self)
        self.prompt = '(Prudentia > Vagrant) '
        self.provider = VagrantProvider()


class VagrantProvider(FactoryProvider):
    NAME = 'vagrant'
    VAGRANT_FILE_NAME = 'Vagrantfile'
    ENV_DIR = path.join(PrudentiaEnv.DEFAULT_ENVS_PATH, NAME)
    CONF_FILE = path.join(ENV_DIR, VAGRANT_FILE_NAME)

    DEFAULT_USER = 'vagrant'
    DEFAULT_PWD = 'vagrant'
    DEFAULT_UBUNTU_DIST_NAME = 'trusty'

    def __init__(self):
        super(VagrantProvider, self).__init__(self.NAME, box_extra_type=VagrantExt)
        this_path = path.dirname(path.realpath(__file__))
        self.template_env = Environment(
            loader=FileSystemLoader(this_path),
            auto_reload=True,
            undefined=jinja2.StrictUndefined
        )
        # BashCmd(path.join(this_path, 'install_vagrant.sh')).execute()

    def register(self):
        try:
            vagrant_boxes = self._action(action="box", action_args=("list",), output=False).splitlines()
            if not vagrant_boxes:
                print '\nThere are no available Vagrant (base) boxes, please search for a suitable one at ' \
                      'https://atlas.hashicorp.com/boxes/search.'
                print 'Once you\'ve chosen the <box> add it using the following cmd \'$ vagrant box add <box>\'.\n'
            else:
                playbook = io.input_path('playbook path')
                hostname = self.fetch_box_hostname(playbook)
                name = io.input_value('box name', self.suggest_name(hostname))
                ip = io.input_value('internal IP')

                ext = VagrantExt()

                mem = io.input_value('amount of RAM in GB', 1)
                ext.set_mem(mem * 1024)

                ext.set_shares(self._input_shares())

                (img, provider) = self._input_img(vagrant_boxes)
                ext.set_image(img)
                ext.set_provider(provider)

                box = Box(name, playbook, hostname, ip, self.DEFAULT_USER, self.DEFAULT_PWD, ext)
                self.add_box(box)
                print "\nBox %s added." % box
        except Exception as e:
            logging.exception('Box not added.')
            print '\nError: %s\n' % e

    def add_box(self, box):
        SimpleProvider.add_box(self, box)
        self.create(box)

    def remove_box(self, box):
        b = super(VagrantProvider, self).remove_box(box)
        self._generate_vagrant_file()
        return b

    def reconfigure(self, previous_box):
        try:
            self.remove_box(previous_box)

            playbook = io.input_path('playbook path', previous_box.playbook)
            hostname = self.fetch_box_hostname(playbook)
            ip = io.input_value('internal IP', previous_box.ip)

            ext = VagrantExt()
            mem = io.input_value('amount of RAM in GB', previous_box.extra.mem / 1024)
            ext.set_mem(mem * 1024)

            ext.set_shares(self._input_shares())
            ext.set_image(previous_box.extra.image)
            ext.set_provider(previous_box.extra.provider)

            box = Box(previous_box.name, playbook, hostname, ip, self.DEFAULT_USER, self.DEFAULT_PWD, ext)
            self.add_box(box)
            print "\nBox %s reconfigured." % box
        except Exception as e:
            logging.exception('Box not reconfigured.')
            print '\nError: %s\n' % e

    def _input_shares(self):
        shares = []
        loop = True
        while loop:
            if io.input_yes_no('share a folder'):
                src = io.input_path('directory on the HOST machine', is_file=False)
                if not path.exists(src):
                    raise ValueError("Directory '%s' on the HOST machine doesn't exists." % src)
                dst = io.input_value('directory on the GUEST machine')
                shares.append((src, dst))
            else:
                loop = False
        return shares

    def _input_img(self, vagrant_boxes):
        available_imgs = {}
        default_trusty_img = None
        for i in vagrant_boxes:
            pattern = '(.*)\s*\((.*),.*\)'
            match = re.match(pattern, i, re.DOTALL)
            img_name = match.group(1).strip()
            img_provider = match.group(2).strip()
            available_imgs[img_name] = img_provider
            if self.DEFAULT_UBUNTU_DIST_NAME in img_name:
                default_trusty_img = img_name

        print '\nAvailable images:'
        for i, p in available_imgs.iteritems():
            print '{0} ({1})'.format(i, p)
        img = io.input_choice('(base) box', default_trusty_img, choices=available_imgs.keys())

        return img, available_imgs[img]

    def _generate_vagrant_file(self):
        env = self.template_env
        template_name = self.VAGRANT_FILE_NAME + '.j2'
        template = env.get_template(template_name)
        template.stream({
            'boxes': self.boxes()
        }).dump(self.CONF_FILE)

    def create(self, box):
        self._generate_vagrant_file()
        self.start(box)

    def start(self, box):
        self._action(action="up", action_args=("--no-provision", box.name))

    def stop(self, box):
        self._action(action="halt", action_args=(box.name,))

    def destroy(self, box):
        if io.input_yes_no('destroy the instance \'{0}\''.format(box.name)):
            self._action(action="destroy", action_args=("-f", box.name))

    def status(self, box):
        output = self._action(action="status", action_args=(box.name,), output=False)
        pattern = '.*' + box.name + '\s*(.*?) \(virtualbox\).*'
        match = re.match(pattern, output, re.DOTALL)
        print match.group(1)

    def _action(self, **kwargs):
        if 'action_args' not in kwargs.keys():
            cmd = BashCmd("vagrant", kwargs['action'])
        else:
            cmd = BashCmd("vagrant", kwargs['action'], *kwargs['action_args'])

        cmd.set_cwd(self.ENV_DIR)
        if 'output' in kwargs.keys():
            cmd.set_show_output(kwargs['output'])
        if 'tags' in kwargs.keys():
            cmd.set_env_var("TAGS", kwargs['tags'])

        # for debugging
        # cmd.set_env_var("VAGRANT_LOG", "INFO")

        cmd.execute()
        if not cmd.is_ok():
            print "ERROR while running: {0}".format(cmd.cmd_args)
        else:
            return cmd.output()


class VagrantExt(object):
    mem = None
    shares = None
    image = None
    provider = None

    def set_mem(self, mem):
        self.mem = mem

    def set_shares(self, shares):
        self.shares = shares

    def set_image(self, img):
        self.image = img

    def set_provider(self, p):
        self.provider = p

    def __repr__(self):
        return 'VagrantExt[mem: %s, shares: %s, image: %s, provider: %s]' % \
               (self.mem, self.shares, self.image, self.provider)

    def to_json(self):
        return {'mem': self.mem, 'shares': self.shares, 'image': self.image, 'provider': self.provider}

    @staticmethod
    def from_json(json):
        e = VagrantExt()
        e.set_mem(json['mem'])
        e.set_shares(json['shares'])
        e.set_image(json['image'])
        e.set_provider(json['provider'])
        return e
