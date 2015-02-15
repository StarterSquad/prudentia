import logging
import time

import ansible.constants as C
from ansible.runner import Runner

from dopy.manager import DoManager, DoError
from domain import Box
from factory import FactoryProvider, FactoryCli
from utils.provisioning import run_module, local_inventory, create_user
from utils.io import input_yes_no, input_value, input_path, xstr


class DigitalOceanCli(FactoryCli):
    def __init__(self):
        FactoryCli.__init__(self)
        self.prompt = '(Prudentia > DigitalOcean) '
        self.provider = DigitalOceanProvider()


class DigitalOceanProvider(FactoryProvider):
    NAME = 'digital-ocean'

    DEFAULT_IMAGE_ID = 9801950  # Ubuntu 14.04 x64
    DEFAULT_SIZE_ID = 63  # 1GB
    DEFAULT_REGION_ID = 5  # Amsterdam 2

    def __init__(self):
        super(DigitalOceanProvider, self).__init__(self.NAME, DOGeneral, DOExt)
        if not self.env.initialized:
            g = self._input_general_env_conf()
        else:
            g = self.env.general
        self.manager = DoManager(g.client_id, g.api_key)

    def _input_general_env_conf(self):
        print '\nThis is the first time you use the Digital Ocean provider, please supply your credentials:'
        client_id = input_value('client id')
        api_key = input_value('api key')
        do_general = DOGeneral(client_id, api_key)
        self.env.set_general(do_general)
        return do_general

    def register(self):
        try:
            name = None
            ip = None
            ext = DOExt()

            if input_yes_no('register an existing droplet'):
                droplet_id = input_value('droplet id')
                droplet_info = self.manager.show_droplet(droplet_id)
                ext.id = droplet_id
                name = droplet_info['name']
                created = droplet_info['created_at']
                print '\nFound droplet \'{0}\' (created {1})'.format(name, created)
                ip = xstr(droplet_info['ip_address'])
                print 'IP: %s' % ip
                ext.image = droplet_info['image_id']
                print 'Image: %s' % ext.image
                ext.size = droplet_info['size_id']
                print 'Size: %s' % ext.size
                ext.region = droplet_info['region_id']
                print 'Region: %s\n' % ext.region

            playbook = input_path('absolute playbook path')
            hostname = self.fetch_box_hostname(playbook)

            if not name:
                name = input_value('box name', self.suggest_name(hostname))

            user = input_value('remote user', C.active_user)

            if not ext.image:
                all_images = self.manager.all_images()
                print '\nAvailable images: \n%s' % self._print_object_id_name(all_images)
                ext.image = input_value('image', self.DEFAULT_IMAGE_ID)

            if not ext.size:
                all_sizes = self.manager.sizes()
                print '\nAvailable sizes: \n%s' % self._print_object_id_name(all_sizes)
                ext.size = input_value('size', self.DEFAULT_SIZE_ID)

            if not ext.region:
                all_regions = self.manager.all_regions()
                print '\nAvailable regions: \n%s' % self._print_object_id_name(all_regions)
                ext.region = input_value('region', self.DEFAULT_REGION_ID)

            if not ext.keys:
                all_keys = self.manager.all_ssh_keys()
                print '\nAvailable keys: \n%s' % self._print_object_id_name(all_keys)
                default_keys = ','.join([str(k['id']) for k in all_keys])
                ext.keys = input_value('keys', default_keys)

            box = Box(name, playbook, hostname, ip, user, extra=ext)
            self.add_box(box)
            print "\nBox %s added." % box
        except Exception as e:
            logging.exception('Box not added.')
            print '\nError: %s\n' % e

    def _print_object_id_name(self, objs):
        return '\n'.join([str(o['id']) + ' -> ' + o['name'] for o in objs])

    def _find_object_name(self, objs, id):
        return next(o for o in objs if o['id'] == id)['name']

    def reconfigure(self, previous_box):
        try:
            self.remove_box(previous_box)

            playbook = input_path('absolute playbook path', previous_box.playbook)
            hostname = self.fetch_box_hostname(playbook)
            ip = previous_box.ip
            user = input_value('remote user', previous_box.remote_user)

            if not previous_box.extra.id:
                ext = DOExt()
                ext.id = previous_box.extra.id
                all_images = self.manager.all_images()
                print '\nAvailable images: \n%s' % self._print_object_id_name(all_images)
                ext.image = input_value('image', previous_box.extra.image)

                all_sizes = self.manager.sizes()
                print '\nAvailable sizes: \n%s' % self._print_object_id_name(all_sizes)
                ext.size = input_value('size', previous_box.extra.size)

                all_keys = self.manager.all_ssh_keys()
                print '\nAvailable keys: \n%s' % self._print_object_id_name(all_keys)
                ext.keys = input_value('keys', previous_box.extra.keys)

                all_regions = self.manager.all_regions()
                print '\nAvailable regions: \n%s' % self._print_object_id_name(all_regions)
                ext.region = input_value('region', previous_box.extra.region)
            else:
                ext = previous_box.extra

            box = Box(previous_box.name, playbook, hostname, ip, user, extra=ext)
            self.add_box(box)
            print "\nBox %s reconfigured." % box
        except Exception as e:
            logging.exception('Box not reconfigured.')
            print '\nError: %s\n' % e

    def add_box(self, box):
        if not box.ip:
            self.create(box)
        super(FactoryProvider, self).add_box(box)

    def create(self, box):
        g = self.env.general
        e = box.extra
        if not e.id:
            print '\nCreating instance \'{0}\' ...'.format(box.name)
            success, result = run_module(Runner(
                transport='local',
                inventory=local_inventory(),
                remote_user='root',
                module_name='digital_ocean',
                module_args='state=present command=droplet client_id={0} api_key={1} '
                            'name={2} size_id={3} image_id={4} region_id={5} ssh_key_ids={6} wait_timeout=300'
                .format(g.client_id, g.api_key, box.name, e.size, e.image, e.region, e.keys))
            )

            droplet = result['droplet']
            box.extra.id = droplet['id']
            box.ip = droplet['ip_address']
            print 'Droplet created with id: {0} -> {1}\n'.format(box.extra.id, box.ip)
        else:
            info = self.manager.show_droplet(e.id)
            print 'Droplet {0} already exists - status: {1}.'.format(e.id, info['status'])
        create_user(box)

    def start(self, box):
        box_id = box.extra.id
        print 'Starting droplet %s ...' % box_id
        self.manager.power_on_droplet(box_id)
        self._wait_to_be_active(box_id)

    def stop(self, box):
        box_id = box.extra.id
        print 'Stopping droplet %s ...' % box_id
        self.manager.power_off_droplet(box_id)

    def destroy(self, box):
        if input_yes_no('destroy the droplet \'{0}\''.format(box.name)):
            box_id = box.extra.id
            box.ip = None
            box.extra.id = None
            print 'Destroying droplet %s ...' % box_id
            self.manager.destroy_droplet(box_id, scrub_data=True)

    def rebuild(self, box):
        e = box.extra
        print 'Rebuilding droplet %s ...' % e.id
        self.manager.rebuild_droplet(e.id, e.image)
        self._wait_to_be_active(e.id)
        create_user(box)

    def _wait_to_be_active(self, droplet_id, wait_timeout=300):
        end_time = time.time() + wait_timeout
        while time.time() < end_time:
            print 'Waiting for droplet %s to be active ...' % droplet_id
            time.sleep(min(20, end_time - time.time()))

            droplet = self.manager.show_droplet(droplet_id)
            if droplet['status'] == 'active':
                droplet_ip_address = droplet['ip_address']
                if not droplet_ip_address:
                    raise DoError('No ip is found.', droplet_id)
                print '\nDroplet %s is now active with ip %s\n' % (droplet_id, droplet_ip_address)
                time.sleep(10)  # Wait for some network latency ...
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

    def __repr__(self):
        return 'DOExt[id: %s, image: %s, size: %s, keys: %s, region: %s]' % (
            self.id, self.image, self.size, self.keys, self.region)

    def to_json(self):
        return {'id': self.id, 'image': self.image, 'size': self.size, 'keys': self.keys, 'region': self.region}

    @staticmethod
    def from_json(json):
        e = DOExt()
        e.id = json['id']
        e.image = json['image']
        e.size = json['size']
        e.keys = json['keys']
        e.region = json['region']
        return e
