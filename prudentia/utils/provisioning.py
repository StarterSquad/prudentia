from datetime import datetime
from random import randint

import ansible.constants as C
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from bunch import Bunch


def run_playbook(playbook_file, inventory, vault_password, remote_user=C.DEFAULT_REMOTE_USER,
                 remote_pass=C.DEFAULT_REMOTE_PASS, transport=C.DEFAULT_TRANSPORT,
                 extra_vars=None, only_tags=None):
    loader = DataLoader()
    loader.set_vault_password(vault_password)

    variable_manager = VariableManager()
    variable_manager.extra_vars = extra_vars

    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=inventory)
    variable_manager.set_inventory(inventory)

    options = Bunch()
    options.remote_user = remote_user
    options.connection = transport
    options.tags = only_tags
    options.listhosts = False
    options.listtasks = False
    options.listtags = False

    options.syntax = None
    options.private_key_file = None
    options.ssh_common_args = None
    options.sftp_extra_args = None
    options.scp_extra_args = None
    options.ssh_extra_args = None
    options.become = None
    options.become_method = 'sudo'
    options.become_user = 'root'

    options.verbosity = 1
    options.check = None

    options.module_path = None
    options.forks = 5

    pbex = PlaybookExecutor(
        playbooks=[playbook_file],
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        options=options,
        passwords={'conn_pass': remote_pass} if remote_pass else {}
    )

    start = datetime.now()

    results = pbex.run()

    print "Play run took {0} minutes\n".format((datetime.now() - start).seconds / 60)

    return results == 0


def run_modules(items):
    for item in items:
        print item['summary']
        success, result = run_module(item['module'])
        if not success:
            return False
    return True


def run_module(runner):
    module_success = True
    module_result = ''
    results = runner.run()
    if not len(results['contacted']):
        module_success = False
        print 'Host not contacted: %s' % results
    else:
        for (hostname, result) in results['contacted'].items():
            if 'failed' in result:
                module_success = False
                module_result = result['msg']
                print 'Run failed: %s' % result['msg']
            else:
                module_result = result
    return module_success, module_result


def generate_inventory(box):
    if box.ip.startswith("./") or box.ip.startswith("/"):
        tmp_inventory = box.ip
    else:
        tmp_inventory = '/tmp/prudentia-inventory-' + str(randint(1, 999999))
        f = None
        try:
            f = open(tmp_inventory, 'w')
            f.write(box.inventory())
        except IOError, ex:
            print ex
        finally:
            f.close()
    # return Inventory(tmp_inventory)
    return tmp_inventory


def create_user(box):
    user = box.remote_user
    if 'root' not in user:
        if 'jenkins' in user:
            user_home = '/var/lib/jenkins'
        else:
            user_home = '/home/' + user

        inventory = generate_inventory(box)
        run_modules([
            {
                'summary': 'Wait for SSH port to become open ...',
                'module': Runner(
                    pattern='localhost',
                    inventory=inventory,
                    module_name='wait_for',
                    module_args='host={0} port=22 delay=10 timeout=60'.format(box.ip)
                )
            },
            {
                'summary': 'Creating group \'{0}\' ...'.format(user),
                'module': Runner(
                    pattern=box.hostname,
                    inventory=inventory,
                    remote_user='root',
                    module_name='group',
                    module_args='name={0} state=present'.format(user)
                )
            },
            {
                'summary': 'Creating user \'{0}\' ...'.format(user),
                'module': Runner(
                    pattern=box.hostname,
                    inventory=inventory,
                    remote_user='root',
                    module_name='user',
                    module_args='state=present shell=/bin/bash generate_ssh_key=yes '
                                'name={0} home={1} group={0} groups=sudo'.format(user, user_home)
                )
            },
            {
                'summary': 'Copy authorized_keys from root ...',
                'module': Runner(
                    pattern=box.hostname,
                    inventory=inventory,
                    remote_user='root',
                    module_name='command',
                    module_args="cp /root/.ssh/authorized_keys {0}/.ssh/authorized_keys".format(
                        user_home)
                )
            },
            {
                'summary': 'Set permission on authorized_keys ...',
                'module': Runner(
                    pattern=box.hostname,
                    inventory=inventory,
                    remote_user='root',
                    module_name='file',
                    module_args="path={0}/.ssh/authorized_keys mode=600 owner={1} group={1}".format(
                        user_home, user)
                )
            },
            {
                'summary': 'Ensuring sudoers no pwd prompting ...',
                'module': Runner(
                    pattern=box.hostname,
                    inventory=inventory,
                    remote_user='root',
                    module_name='lineinfile',
                    module_args="dest=/etc/sudoers state=present regexp=%sudo "
                                "line='%sudo ALL=(ALL:ALL) NOPASSWD:ALL' validate='visudo -cf %s'"
                )
            }
        ])


def gather_facts(box, filter_value):
    return run_module(
        Runner(
            pattern=box.hostname,
            inventory=generate_inventory(box),
            remote_user=box.get_remote_user(),
            remote_pass=box.get_remote_pwd(),
            transport=box.get_transport(),
            module_name='setup',
            module_args='filter=' + filter_value
        )
    )
