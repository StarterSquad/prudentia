#!/usr/bin/python
# -*- coding: utf-8 -*-

# [..] various imports

# this line must be written exactly that way,
# as Ansible will replace it with the "imported" code
from ansible.module_utils.basic import *

ANSIBLE_HASHI_VAULT_ADDR = 'http://127.0.0.1:8200'

if os.getenv('VAULT_ADDR') is not None:
    ANSIBLE_HASHI_VAULT_ADDR = os.environ['VAULT_ADDR']


class HashiVaultFile:
    def __init__(self, **kwargs):
        try:
            import hvac
        except ImportError:
            raise Exception("Please pip install hvac to use this module")

        self.url = kwargs.pop('url')
        self.secret = kwargs.pop('secret')
        self.token = kwargs.pop('token')

        self.client = hvac.Client(url=self.url, token=self.token)

        if self.client.is_authenticated():
            pass
        else:
            raise Exception("Invalid Hashicorp Vault Token Specified")

    def get(self):
        data = self.client.read(self.secret)
        if data is None:
            raise Exception("The secret %s doesn't seem to exist" % self.secret)
        else:
            return data['data']['value']


if __name__ == '__main__':
    global module
    module = AnsibleModule(
        argument_spec={
            'secret': {'required': True, 'type': 'str'},
            'dest': {'required': True, 'type': 'str'},
            'token': {'required': False, 'type': 'str'},
        },
        supports_check_mode=False
    )

    args = module.params

    args['url'] = ANSIBLE_HASHI_VAULT_ADDR
    try:
        vault_conn = HashiVaultFile(**args)
        value = vault_conn.get()

        dest_file = os.path.abspath(args['dest'])

        text_file = open(dest_file, "w")
        text_file.write(value)
        text_file.close()

        module.exit_json(changed=True, file=dest_file)
    except Exception, e:
        module.fail_json(msg=str(e))
