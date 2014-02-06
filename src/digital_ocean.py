import logging
import time

import ansible.constants as C

from dopy.manager import DoManager, DoError
from domain import Box
from factory import FactoryProvider
from utils.io import input_string, input_yes_no


class DigitalOceanProvider(FactoryProvider):
    NAME = 'digital-ocean'
    ENV_DIR = './env/' + NAME
    PLAYBOOK_TEMPLATE = 'do.yml'
    PLAYBOOK_FILE = ENV_DIR + '/' + PLAYBOOK_TEMPLATE

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
            # TODO register using existing id (or name) ?

            playbook = input_string('playbook path')
            hostname = self.fetch_box_hostname(playbook)
            name = input_string('box name', default_value=self.suggest_name(hostname))
            ip = 'localhost'
            user = input_string('remote user', default_value=C.active_user)

            ext = DOExt()
            ext.set_image(input_string('image', default_description='Ubuntu 12.04.3 x64', default_value='1505447',
                                       mandatory=True))

            all_sizes = self.manager.sizes()
            print '\nAvailable sizes: \n%s' % self._print_id_name(all_sizes)
            ext.set_size(input_string('size', default_description='1GB', default_value='63', mandatory=True))

            all_keys = self.manager.all_ssh_keys()
            default_keys = ', '.join([str(k['id']) for k in all_keys])
            print '\nAvailable keys: \n%s' % self._print_id_name(all_keys)
            ext.set_keys(input_string('keys', default_description='All', default_value=default_keys, mandatory=True))

            all_regions = self.manager.all_regions()
            print '\nAvailable regions: \n%s' % self._print_id_name(all_regions)
            ext.set_region(input_string('region', default_description='Amsterdam 2', default_value='5', mandatory=True))

            box = Box(name, playbook, hostname, ip, user, extra=ext)
            self.add_box(box)
            print "\nBox %s added." % box
        except Exception as e:
            logging.exception('Box not added.')
            print '\nThere was some problem while adding the box: %s\n' % e

    def _print_id_name(self, objs):
        return '\n'.join([str(o['id']) + ' -> ' + o['name'] for o in objs])

    def reconfigure(self, box):
        # TODO
        pass

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
