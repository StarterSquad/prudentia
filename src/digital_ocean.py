import os

from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from domain import Box
from factory import FactoryProvider
from util import input_string


class DigitalOceanProvider(FactoryProvider):
    NAME = 'digital-ocean'
    ENV_DIR = './env/' + NAME
    PLAYBOOK_TEMPLATE = 'do.yml'
    PLAYBOOK_FILE = ENV_DIR + '/' + PLAYBOOK_TEMPLATE

    def __init__(self):
        super(DigitalOceanProvider, self).__init__(self.NAME, DigitalOceanExt)
        self.template_env = Environment(loader=FileSystemLoader('./src'), auto_reload=True)
        self._generate_playbook_file()

    def _generate_playbook_file(self):
        if not os.path.exists(self.PLAYBOOK_FILE):
            client_id = input_string('client id')
            api_key = input_string('api key')
            template = self.template_env.get_template(self.PLAYBOOK_TEMPLATE + '.j2')
            template.stream({
                'client_id': client_id,
                'api_key': api_key
            }).dump(self.PLAYBOOK_FILE)

    def register(self):
        try:
            # TODO register using existing id (or name) ?

            playbook = input_string('playbook path')
            name = self.fetch_box_name(playbook)
            ip = 'localhost'

            ext = DigitalOceanExt()
            ext.set_image(input_string('image', default_description='Ubuntu 12.04.3 x64', default_value='1505447', mandatory=True))
            # Size id: 66 -> 512MB, 63 ->1GB, 62 -> 2GB
            ext.set_size(input_string('size', default_description='1 GB', default_value='63', mandatory=True))
            # Ssh keys: 57850 -> Tiziano, 58730 -> Dmitry, 58739 -> Iwein
            ext.set_keys(input_string('keys', default_description='Tiziano,Dmitry,Iwein', default_value='57850,58730,58739', mandatory=True))
            # Region id: 2 -> Amsterdam 1, 5 -> Amsterdam 2
            ext.set_region(input_string('region', default_description='Ams 2', default_value='5', mandatory=True))

            box = Box(name, playbook, ip, extra=ext)
            self.add_box(box)
            print "\nBox %s added." % box
        except Exception as e:
            print '\nThere was some problem while adding the box: %s\n' % e

    def reconfigure(self, box_name):
        # TODO
        pass

    def create(self, box_name):
        box = self.env.get(box_name)
        droplet = {
            'droplet_name': box.name,
            'droplet_image': box.extra.image,
            'droplet_size': box.extra.size,
            'droplet_keys': box.extra.keys,
            'droplet_region': box.extra.region
        }

        self.run_playbook(
            playbook_file=self.PLAYBOOK_FILE,
            inventory=self._generate_inventory(box),
            transport='local',
            extra_vars=dict(self.extra_vars.items() + droplet.items()),
            only_tags=['create']
        )

    def start(self, box_name):
        # TODO
        pass

    def stop(self, box_name):
        # TODO
        pass

    def destroy(self, box_name):
        # TODO
        pass


class DigitalOceanExt(object):
    image = None
    size = None
    keys = None
    region = None

    def set_image(self, image):
        self.image = image

    def set_size(self, size):
        self.size = size

    def set_keys(self, keys):
        self.keys = keys

    def set_region(self, region):
        self.region = region

    def __repr__(self):
        return 'DigitalOceanExt[image: %s, size: %s, keys: %s, region: %s]' % (self.image, self.size, self.keys, self.region)

    def to_json(self):
        return {'image': self.image, 'size': self.size, 'keys': self.keys, 'region': self.region}

    @staticmethod
    def from_json(json):
        e = DigitalOceanExt()
        e.set_image(json['image'])
        e.set_size(json['size'])
        e.set_keys(json['keys'])
        e.set_region(json['region'])
        return e
