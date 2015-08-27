import logging
import time

import ansible.constants as C

from dopy.manager import DoManager, DoError
from domain import Box
from factory import FactoryProvider, FactoryCli
from simple import SimpleProvider
from utils.provisioning import create_user
from utils.io import input_yes_no, input_value, input_path, xstr, input_choice


class DigitalOceanCli(FactoryCli):
    def __init__(self):
        FactoryCli.__init__(self)
        self.prompt = '(Prudentia > DigitalOcean) '
        self.provider = DigitalOceanProvider()


class DigitalOceanProvider(FactoryProvider):
    NAME = 'digital-ocean'

    DEFAULT_IMAGE_NAME = "14.04 x64"  # Ubuntu latest LTS 64bit
    DEFAULT_SIZE_SLUG = "1gb"
    DEFAULT_REGION_SLUG = "ams3"

    def __init__(self):
        super(DigitalOceanProvider, self).__init__(self.NAME, DOGeneral, DOExt)
        if (not self.env.initialized) or (not self.env.general) or (not self.env.general.api_token):
            g = self._input_general_env_conf()
        else:
            g = self.env.general
        self.manager = DoManager(None, g.api_token, api_version=2)

    def _input_general_env_conf(self):
        print '\nThe DigitalOcean API (v2) token is not configured, if you don\'t have one please visit https://cloud.digitalocean.com/settings/applications and generate it.'
        api_token = input_value('api token')
        do_general = DOGeneral(api_token)
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
                ext.image = droplet_info['image']['id']
                print 'Image: %s' % ext.image
                ext.size = droplet_info['size']['slug']
                print 'Size: %s' % ext.size
                ext.region = droplet_info['region']['slug']
                print 'Region: %s\n' % ext.region

            playbook = input_path('playbook path')
            hostname = self.fetch_box_hostname(playbook)

            if not name:
                name = input_value('box name', self.suggest_name(hostname))

            user = input_value('remote user', C.active_user)

            if not ext.image:
                all_images = self.manager.all_images()
                print '\nAvailable images: \n%s' % self._print_object_id_name(all_images)
                default_image = next((img for img in all_images if self.DEFAULT_IMAGE_NAME in img['name']), None)
                image_desc = '{0} - {1} {2}'.format(default_image['id'], default_image['distribution'], default_image['name'])
                ext.image = input_value('image', default_image['id'], image_desc)

            if not ext.size:
                all_sizes = self.manager.sizes()
                sizes_slug = [o['slug'] for o in all_sizes]
                print '\nAvailable sizes: \n%s' % '\n'.join(sizes_slug)
                ext.size = input_choice('size', self.DEFAULT_SIZE_SLUG, choices=sizes_slug)

            if not ext.region:
                all_regions = self.manager.all_regions()
                regions_slug = [o['slug'] for o in all_regions]
                print '\nAvailable regions: \n%s' % '\n'.join(regions_slug)
                ext.region = input_choice('region', self.DEFAULT_REGION_SLUG, choices=regions_slug)

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

    def reconfigure(self, previous_box):
        try:
            self.remove_box(previous_box)

            playbook = input_path('playbook path', previous_box.playbook)
            hostname = self.fetch_box_hostname(playbook)
            ip = previous_box.ip
            user = input_value('remote user', previous_box.remote_user)

            if not previous_box.extra.id:
                ext = DOExt()
                ext.id = previous_box.extra.id
                all_images = self.manager.all_images()
                print '\nAvailable images: \n%s' % self._print_object_id_name(all_images)
                prev_image = next((img for img in all_images if previous_box.extra.image == img['id']), None)
                if prev_image:
                    prev_image_desc = '{0} - {1} {2}'.format(prev_image['id'], prev_image['distribution'], prev_image['name'])
                    ext.image = input_value('image', prev_image['id'], prev_image_desc)
                else:
                    ext.image = input_value('image')

                all_sizes = self.manager.sizes()
                sizes_slug = [o['slug'] for o in all_sizes]
                print '\nAvailable sizes: \n%s' % '\n'.join(sizes_slug)
                ext.size = input_value('size', previous_box.extra.size)

                all_regions = self.manager.all_regions()
                regions_slug = [o['slug'] for o in all_regions]
                print '\nAvailable regions: \n%s' % '\n'.join(regions_slug)
                ext.region = input_value('region', previous_box.extra.region)

                all_keys = self.manager.all_ssh_keys()
                print '\nAvailable keys: \n%s' % self._print_object_id_name(all_keys)
                ext.keys = input_value('keys', previous_box.extra.keys)
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
        SimpleProvider.add_box(self, box)

    def create(self, box):
        e = box.extra
        if not e.id:
            print '\nCreating instance \'{0}\' ...'.format(box.name)
            droplet = self.manager.new_droplet(name=box.name, size_id=e.size, image_id=e.image, region_id=e.region,
                                               ssh_key_ids=e.keys.split(','))
            box.extra.id = droplet['id']
            box.ip = self._wait_to_be_active(box.extra.id)
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

    def status(self, box):
        print self.manager.show_droplet(box.extra.id)['status']

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
    def __init__(self, api_token):
        self.api_token = api_token

    def __repr__(self):
        return 'DOGeneral[api_token: %s]' % self.api_token

    def to_json(self):
        return {'api_token': self.api_token}

    @staticmethod
    def from_json(json):
        return DOGeneral(json.get('api_token'))


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
