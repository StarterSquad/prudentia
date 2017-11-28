import os
import tempfile
from datetime import datetime

import ansible.constants as C
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.playbook import Play
from bunch import Bunch
from prudentia.utils import io

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

VERBOSITY = 0


def run_playbook(playbook_file, inventory_file, loader, remote_user=C.DEFAULT_REMOTE_USER,
                 remote_pass=C.DEFAULT_REMOTE_PASS, transport=C.DEFAULT_TRANSPORT,
                 extra_vars=None, only_tags=None):
    variable_manager = get_variable_manager(loader)
    variable_manager.extra_vars = {} if extra_vars is None else extra_vars

    loader._FILE_CACHE = dict()  # clean up previously read and cached files
    inv = get_inventory(loader=loader, variable_manager=variable_manager, inventory_file=inventory_file)
    variable_manager.set_inventory(inv)

    options = default_options(remote_user, transport, only_tags)
    display.verbosity = options.verbosity
    pbex = PlaybookExecutor(
        playbooks=[playbook_file],
        inventory=inv,
        variable_manager=variable_manager,
        loader=loader,
        options=options,
        passwords={'conn_pass': remote_pass} if remote_pass else {}
    )

    start = datetime.now()
    results = pbex.run()
    print "Play run took {0} minutes\n".format((datetime.now() - start).seconds / 60)

    return results == 0


def run_play(play_ds, inventory_file, loader, remote_user, remote_pass, transport, extra_vars=None):
    variable_manager = get_variable_manager(loader)
    variable_manager.extra_vars = {} if extra_vars is None else extra_vars

    loader._FILE_CACHE = dict()  # clean up previously read and cached files
    inv = get_inventory(loader=loader, variable_manager=variable_manager, inventory_file=inventory_file)
    variable_manager.set_inventory(inv)

    play = Play.load(play_ds, variable_manager=variable_manager, loader=loader)

    tqm = None
    result = 1
    try:
        options = default_options(remote_user, transport)
        display.verbosity = options.verbosity
        tqm = TaskQueueManager(
            inventory=inv,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords={'conn_pass': remote_pass} if remote_pass else {},
            stdout_callback='minimal',
            run_additional_callbacks=C.DEFAULT_LOAD_CALLBACK_PLUGINS,
            run_tree=False,
        )
        result = tqm.run(play)
    except Exception, ex:
        io.track_error('cannot run play', ex)
    finally:
        if tqm:
            tqm.cleanup()

    return result == 0


def get_variable_manager(loader):
    try:
        # Ansible 2.4
        from ansible.vars.manager import VariableManager
        return VariableManager(loader)
    except:
        # Ansible 2.3
        from ansible.vars import VariableManager
        return VariableManager()


def get_inventory(loader, variable_manager, inventory_file):
    try:
        # Ansible 2.4
        from ansible.inventory.manager import InventoryManager
        return InventoryManager(
            loader=loader,
            sources=inventory_file
        )
    except:
        # Ansible 2.3
        from ansible import inventory
        inventory.HOSTS_PATTERNS_CACHE = {}  # clean up previous cached hosts
        return inventory.Inventory(
            loader=loader,
            variable_manager=variable_manager,
            host_list=inventory_file
        )


def default_options(remote_user, transport, only_tags=None):
    if only_tags is None:
        only_tags = []

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
    options.ssh_extra_args = ''
    options.ssh_common_args = ''
    options.ssh_args = ''
    options.become = None
    options.become_method = 'sudo'
    options.become_user = 'root'

    options.verbosity = VERBOSITY
    options.check = None
    options.diff = None

    options.module_path = None
    options.forks = 5

    return options


def generate_inventory(box):
    if box.ip.startswith("./") or box.ip.startswith("/"):
        tmp_inventory = box.ip
    else:
        fd, tmp_inventory = tempfile.mkstemp(prefix='prudentia-inventory-')
        try:
            os.write(fd, box.inventory())
        except IOError, ex:
            io.track_error('cannot write inventory file', ex)
        finally:
            os.close(fd)
    return tmp_inventory


def create_user(box, loader):
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
                tasks=loader.load_from_file(sudo_user_play)
            ),
            inventory_file=generate_inventory(box),
            loader=loader,
            remote_user='root',
            remote_pass=box.get_remote_pwd(),
            transport=box.get_transport(),
            extra_vars={'ssh_seed_user': 'root', 'user': user, 'group': user, 'home': user_home}
        )
    else:
        print 'Root user cannot be created!'

    return res


def gather_facts(box, filter_value, loader):
    return run_play(
        play_ds=dict(
            hosts=box.hostname,
            gather_facts='no',
            tasks=[{'setup': 'filter={0}'.format(filter_value)}]
        ),
        inventory_file=generate_inventory(box),
        loader=loader,
        remote_user=box.get_remote_user(),
        remote_pass=box.get_remote_pwd(),
        transport=box.get_transport()
    )
