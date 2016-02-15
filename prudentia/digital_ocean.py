import time

from dopy.manager import DoManager, DoError
from prudentia.domain import Box
from prudentia.factory import FactoryProvider, FactoryCli
from prudentia.simple import SimpleProvider
from prudentia.utils.provisioning import create_user
from prudentia.utils import io


class DigitalOceanCli(FactoryCli):
    def __init__(self):
        FactoryCli.__init__(self)
        self.prompt = '(Prudentia > DigitalOcean) '
        self.provider = DigitalOceanProvider()


class DigitalOceanProvider(FactoryProvider):
    NAME = 'digital-ocean'

    DEFAULT_IMAGE_SLUG = "ubuntu-14-04-x64"  # Ubuntu latest LTS 64bit
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
        print '\nThe DigitalOcean API (v2) token is not configured.'
        print 'If you don\'t have it please visit ' \
              'https://cloud.digitalocean.com/settings/applications and generate one.'
        api_token = io.input_value('api token')
        do_general = DOGeneral(api_token)
        self.env.set_general(do_general)
        return do_general

    def define_box(self):
        ip = None
        ext = DOExt()

        if io.input_yes_no('register an existing droplet'):
            droplet_id = io.input_value('droplet id')
            droplet_info = self.manager.show_droplet(droplet_id)
            ext.id = droplet_id
            name = droplet_info['name']
            created = droplet_info['created_at']
            print '\nFound droplet \'{0}\' (created {1})'.format(name, created)
            ip = io.xstr(droplet_info['ip_address'])
            print 'IP: %s' % ip
            ext.image = droplet_info['image']['id']
            print 'Image: %s' % ext.image
            ext.size = droplet_info['size']['slug']
            print 'Size: %s' % ext.size
            ext.region = droplet_info['region']['slug']
            print 'Region: %s\n' % ext.region

            playbook = io.input_path('playbook path')
            hostname = self.fetch_box_hosts(playbook)
            user = io.input_value('remote user', self.active_user)
        else:
            playbook = io.input_path('playbook path')
            hostname = self.fetch_box_hosts(playbook)
            name = io.input_value('box name', self.suggest_name(hostname))
            user = io.input_value('remote user', self.active_user)

            all_images = self.manager.all_images()
            print '\nAvailable images: \n%s' % self._print_object_id_name(all_images)
            default_image = next((img for img in all_images
                                  if self.DEFAULT_IMAGE_SLUG in img['slug']), None)
            if default_image:
                image_desc = '{0} - {1} {2}'.format(
                    default_image['id'],
                    default_image['distribution'],
                    default_image['name']
                )
                ext.image = io.input_value('image', default_image['id'], image_desc)
            else:
                ext.image = io.input_value('image')

            all_sizes = self.manager.sizes()
            sizes_slug = [o['slug'] for o in all_sizes]
            print '\nAvailable sizes: \n%s' % '\n'.join(sizes_slug)
            ext.size = io.input_choice('size', self.DEFAULT_SIZE_SLUG, choices=sizes_slug)

            all_regions = self.manager.all_regions()
            regions_slug = [o['slug'] for o in all_regions]
            print '\nAvailable regions: \n%s' % '\n'.join(regions_slug)
            ext.region = io.input_choice('region', self.DEFAULT_REGION_SLUG, choices=regions_slug)

            ext.keys = self._input_ssh_keys()

        return Box(name, playbook, hostname, ip, user, extra=ext)

    @staticmethod
    def _print_object_id_name(objs):
        def _dist_if_exists(prop):
            return prop['distribution'] + ' ' if 'distribution' in prop else ''

        return '\n'.join([str(o['id']) + ' -> ' + _dist_if_exists(o) + o['name'] for o in objs])

    def redefine_box(self, previous_box):
        playbook = io.input_path('playbook path', previous_box.playbook)
        hostname = self.fetch_box_hosts(playbook)
        ip = previous_box.ip
        user = io.input_value('remote user', previous_box.remote_user)

        if not previous_box.extra.id:
            ext = DOExt()
            ext.id = previous_box.extra.id
            all_images = self.manager.all_images()
            print '\nAvailable images: \n%s' % self._print_object_id_name(all_images)
            prev_image = next((img for img in all_images
                               if previous_box.extra.image == img['id']), None)
            if prev_image:
                prev_image_desc = '{0} - {1} {2}'.format(
                    prev_image['id'],
                    prev_image['distribution'],
                    prev_image['name']
                )
                ext.image = io.input_value('image', prev_image['id'], prev_image_desc)
            else:
                ext.image = io.input_value('image')

            all_sizes = self.manager.sizes()
            sizes_slug = [o['slug'] for o in all_sizes]
            print '\nAvailable sizes: \n%s' % '\n'.join(sizes_slug)
            ext.size = io.input_value('size', previous_box.extra.size)

            all_regions = self.manager.all_regions()
            regions_slug = [o['slug'] for o in all_regions]
            print '\nAvailable regions: \n%s' % '\n'.join(regions_slug)
            ext.region = io.input_value('region', previous_box.extra.region)

            ext.keys = self._input_ssh_keys(previous_box.extra.keys)
        else:
            ext = previous_box.extra

        return Box(previous_box.name, playbook, hostname, ip, user, extra=ext)

    def add_box(self, box):
        if not box.ip:
            self.create(box)
        SimpleProvider.add_box(self, box)

    def create(self, box):
        ext = box.extra
        if not ext.id:
            if not ext.keys:
                print '\nNo valid keys are defined.'
                print 'Please run `reconfigure {0}` to provide them.'.format(box.name)
                return False
            print '\nCreating instance \'{0}\' ...'.format(box.name)
            droplet = self.manager.new_droplet(
                name=box.name, size_id=ext.size,
                image_id=ext.image, region_id=ext.region,
                ssh_key_ids=ext.keys.split(',')
            )
            box.extra.id = droplet['id']
            box.ip = self._wait_to_be_active(box.extra.id)
        else:
            info = self.manager.show_droplet(ext.id)
            print 'Droplet {0} already exists - status: {1}.'.format(ext.id, info['status'])
        create_user(box, self.loader)

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
        if io.input_yes_no('destroy the droplet \'{0}\''.format(box.name)):
            box_id = box.extra.id
            box.ip = None
            box.extra.id = None
            print 'Destroying droplet %s ...' % box_id
            self.manager.destroy_droplet(box_id, scrub_data=True)

    def rebuild(self, box):
        ext = box.extra
        print 'Rebuilding droplet %s ...' % ext.id
        self.manager.rebuild_droplet(ext.id, ext.image)
        self._wait_to_be_active(ext.id)
        create_user(box, self.loader)

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

    def _input_ssh_keys(self, previous=None):
        all_keys = self.manager.all_ssh_keys()
        print '\nAvailable keys: \n%s' % self._print_object_id_name(all_keys)
        if not previous:
            default_keys = ','.join([str(k['id']) for k in all_keys])
        else:
            default_keys = previous
        return io.input_value('keys', default_keys)


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
        return {'id': self.id, 'image': self.image, 'size': self.size,
                'keys': self.keys, 'region': self.region}

    @staticmethod
    def from_json(json):
        ext = DOExt()
        ext.id = json['id']
        ext.image = json['image']
        ext.size = json['size']
        ext.keys = json['keys']
        ext.region = json['region']
        return ext
