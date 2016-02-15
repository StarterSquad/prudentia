import os
from datetime import datetime
from random import randint

import ansible.constants as C
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.playbook import Play
from ansible.vars import VariableManager
from bunch import Bunch
from prudentia.utils import io


def run_playbook(playbook_file, inventory, vault_password, remote_user=C.DEFAULT_REMOTE_USER,
                 remote_pass=C.DEFAULT_REMOTE_PASS, transport=C.DEFAULT_TRANSPORT,
                 extra_vars=None, only_tags=None):
    loader = DataLoader()
    loader.set_vault_password(vault_password)
    variable_manager = VariableManager()
    variable_manager.extra_vars = extra_vars
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=inventory)
    variable_manager.set_inventory(inventory)

    pbex = PlaybookExecutor(
        playbooks=[playbook_file],
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        options=default_options(remote_user, transport, only_tags),
        passwords={'conn_pass': remote_pass} if remote_pass else {}
    )

    start = datetime.now()
    results = pbex.run()
    print "Play run took {0} minutes\n".format((datetime.now() - start).seconds / 60)

    return results == 0


def run_play(play_ds, inventory, remote_user, remote_pass, transport, extra_vars=None):
    loader = DataLoader()
    variable_manager = VariableManager()
    variable_manager.extra_vars = {} if extra_vars is None else extra_vars
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=inventory)
    variable_manager.set_inventory(inventory)

    play = Play().load(play_ds, variable_manager=variable_manager, loader=loader)

    tqm = None
    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=default_options(remote_user, transport),
            passwords={'conn_pass': remote_pass} if remote_pass else {},
            stdout_callback='minimal',
            run_additional_callbacks=C.DEFAULT_LOAD_CALLBACK_PLUGINS,
            run_tree=False,
        )
        result = tqm.run(play)
    finally:
        if tqm:
            tqm.cleanup()

    return result == 0


def default_options(remote_user, transport, only_tags=None):
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

    return options


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
            io.track_error('cannot write invetory file', ex)
        finally:
            f.close()
    return tmp_inventory


def create_user(box):
    res = False

    user = box.remote_user
    if 'root' not in user:
        if 'jenkins' in user:
            user_home = '/var/lib/jenkins'
        else:
            user_home = '/home/' + user

        sudo_user_play = os.path.join(io.prudentia_python_dir(), 'tasks', 'add-sudo-user.yml')
        res = run_play(
            play_ds=dict(
                hosts=box.hostname,
                gather_facts='no',
                tasks=DataLoader().load_from_file(sudo_user_play)
            ),
            inventory=generate_inventory(box),
            remote_user=box.get_remote_user(),
            remote_pass=box.get_remote_pwd(),
            transport=box.get_transport(),
            extra_vars={'user': user, 'group': user, 'home': user_home}
        )
    else:
        print 'Root user cannot be created!'

    return res


def gather_facts(box, filter_value):
    return run_play(
        play_ds=dict(
            hosts=box.hostname,
            gather_facts='no',
            tasks=[{'setup': 'filter={0}'.format(filter_value)}]
        ),
        inventory=generate_inventory(box),
        remote_user=box.get_remote_user(),
        remote_pass=box.get_remote_pwd(),
        transport=box.get_transport()
    )
