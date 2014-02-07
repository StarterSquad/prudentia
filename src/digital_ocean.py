import logging
import time

import ansible.constants as C

from dopy.manager import DoManager, DoError
from domain import Box
from factory import FactoryProvider, FactoryCli
from utils.io import input_string, input_yes_no, input_value


class DigitalOceanCli(FactoryCli):
    def __init__(self):
        FactoryCli.__init__(self)
        self.prompt = '(Prudentia > DigitalOcean) '
        self.provider = DigitalOceanProvider()


class DigitalOceanProvider(FactoryProvider):
    NAME = 'digital-ocean'

    DEFAULT_IMAGE_ID = 1505447  # Ubuntu 12.04.3 x64
    DEFAULT_SIZE_ID = 63        # 1GB
    DEFAULT_REGION_ID = 5       # Amsterdam 2

    def __init__(self):
        super(DigitalOceanProvider, self).__init__(self.NAME, DOGeneral, DOExt)
        if not self.env.initialized:
            g = self._input_general_env_conf()
        else:
            g = self.env.general
        self.manager = DoManager(g.client_id, g.api_key)

    def _input_general_env_conf(self):
        client_id = input_string('client id')
        api_key = input_string('api key')
        do_general = DOGeneral(client_id, api_key)
        self.env.set_general(do_general)
        return do_general

    def register(self):
        try:
            playbook = input_value('playbook path')
            hostname = self.fetch_box_hostname(playbook)
            name = input_value('box name', self.suggest_name(hostname))
            ip = 'TBD'
            user = input_value('remote user', C.active_user)

            ext = DOExt()
            all_images = self.manager.all_images()
            print '\nAvailable images: \n%s' % self._print_object_id_name(all_images)
            ext.set_image(input_value('image', self.DEFAULT_IMAGE_ID))

            all_sizes = self.manager.sizes()
            print '\nAvailable sizes: \n%s' % self._print_object_id_name(all_sizes)
            ext.set_size(input_value('size', self.DEFAULT_SIZE_ID))

            all_keys = self.manager.all_ssh_keys()
            print '\nAvailable keys: \n%s' % self._print_object_id_name(all_keys)
            default_keys = ','.join([str(k['id']) for k in all_keys])
            ext.set_keys(input_value('keys', default_keys))

            all_regions = self.manager.all_regions()
            print '\nAvailable regions: \n%s' % self._print_object_id_name(all_regions)
            ext.set_region(input_value('region', self.DEFAULT_REGION_ID))

            box = Box(name, playbook, hostname, ip, user, extra=ext)
            self.add_box(box)
            print "\nBox %s added." % box
        except Exception as e:
            logging.exception('Box not added.')
            print '\nThere was some problem while adding the box: %s\n' % e

    def _print_object_id_name(self, objs):
        return '\n'.join([str(o['id']) + ' -> ' + o['name'] for o in objs])

    def _find_object_name(self, objs, id):
        return next(o for o in objs if o['id'] == id)['name']

    def reconfigure(self, previous_box):
        try:
            self.remove_box(previous_box)

            playbook = input_value('playbook path', previous_box.playbook)
            hostname = self.fetch_box_hostname(playbook)
            ip = 'TBD'
            user = input_value('remote user', previous_box.remote_user)

            ext = DOExt()
            all_images = self.manager.all_images()
            print '\nAvailable images: \n%s' % self._print_object_id_name(all_images)
            ext.set_image(input_value('image', previous_box.extra.image))

            all_sizes = self.manager.sizes()
            print '\nAvailable sizes: \n%s' % self._print_object_id_name(all_sizes)
            ext.set_size(input_value('size', previous_box.extra.size))

            all_keys = self.manager.all_ssh_keys()
            print '\nAvailable keys: \n%s' % self._print_object_id_name(all_keys)
            ext.set_keys(input_value('keys', previous_box.extra.keys))

            all_regions = self.manager.all_regions()
            print '\nAvailable regions: \n%s' % self._print_object_id_name(all_regions)
            ext.set_region(input_value('region', previous_box.extra.region))

            box = Box(previous_box.name, playbook, hostname, ip, user, extra=ext)
            self.add_box(box)
            print "\nBox %s reconfigured." % box
        except Exception as e:
            logging.exception('Box not reconfigured.')
            print '\nThere was some problem while reconfiguring the box: %s\n' % e

    def create(self, box):
        e = box.extra
        if not e.id:
            print 'Creating instance %s ...' % box.name
            res = self.manager.new_droplet(box.name, e.size, e.image, e.region, e.keys)
            droplet_id = res['id']
            box.extra.set_id(droplet_id)
            print 'Instance created: %s' % droplet_id
        else:
            droplet_id = e.id
            print 'Droplet already created'
        box.ip = self._wait_to_be_active(droplet_id)
        self.create_user(box)

    def start(self, box):
        box_id = box.extra.id
        print 'Starting instance %s ...' % box_id
        self.manager.power_on_droplet(box_id)
        self._wait_to_be_active(box_id)

    def stop(self, box):
        box_id = box.extra.id
        print 'Stopping instance %s ...' % box_id
        self.manager.power_off_droplet(box_id)

    def destroy(self, box):
        if input_yes_no('destroy the instance \'{0}\''.format(box.name)):
            box_id = box.extra.id
            print 'Destroying instance %s ...' % box_id
            self.manager.destroy_droplet(box_id, scrub_data=True)

    def rebuild(self, box):
        e = box.extra
        print 'Rebuilding instance %s ...' % e.id
        self.manager.rebuild_droplet(e.id, e.image)
        self._wait_to_be_active(e.id)
        self.create_user(box)

    def _wait_to_be_active(self, droplet_id, wait_timeout=300):
        end_time = time.time() + wait_timeout
        while time.time() < end_time:
            print 'Waiting for instance %s to be active ...' % droplet_id
            time.sleep(min(20, end_time - time.time()))

            droplet = self.manager.show_droplet(droplet_id)
            if droplet['status'] == 'active':
                droplet_ip_address = droplet['ip_address']
                if not droplet_ip_address:
                    raise DoError('No ip is found.', droplet_id)
                print '\nInstance %s is now active with ip %s\n' % (droplet_id, droplet_ip_address)
                time.sleep(20)  # Wait for SSH to be up
                return droplet_ip_address
        raise DoError('Wait for droplet running timeout', droplet_id)


class DOGeneral(object):
    def __init__(self, client_id, api_key):
        self.client_id = client_id
        self.api_key = api_key

    def __repr__(self):
        return 'DOGeneral[client_id: %s, api_key: %s]' % (self.client_id, self.api_key)

    def to_json(self):
        return {'client_id': self.client_id, 'api_key': self.api_key}

    @staticmethod
    def from_json(json):
        return DOGeneral(json['client_id'], json['api_key'])


class DOExt(object):
    id = None
    image = None
    size = None
    keys = None
    region = None

    def set_id(self, box_id):
        self.id = box_id

    def set_image(self, image):
        self.image = image

    def set_size(self, size):
        self.size = size

    def set_keys(self, keys):
        self.keys = keys

    def set_region(self, region):
        self.region = region

    def __repr__(self):
        return 'DOExt[id: %s, image: %s, size: %s, keys: %s, region: %s]' % (
            self.id, self.image, self.size, self.keys, self.region)

    def to_json(self):
        return {'id': self.id, 'image': self.image, 'size': self.size, 'keys': self.keys, 'region': self.region}

    @staticmethod
    def from_json(json):
        e = DOExt()
        e.set_id(json['id'])
        e.set_image(json['image'])
        e.set_size(json['size'])
        e.set_keys(json['keys'])
        e.set_region(json['region'])
        return e
