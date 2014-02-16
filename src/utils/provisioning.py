import sys
from datetime import datetime

from ansible.inventory import Inventory
from ansible.playbook import PlayBook
from ansible import callbacks, errors
import ansible.constants as C
from ansible.color import stringc

from src.domain import Box


def run_playbook(playbook_file, inventory, remote_user=C.DEFAULT_REMOTE_USER,
                 remote_pass=C.DEFAULT_REMOTE_PASS, transport=C.DEFAULT_TRANSPORT, extra_vars=None, only_tags=None):
    stats = callbacks.AggregateStats()
    playbook_cb = callbacks.PlaybookCallbacks(verbose=True)
    runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=True)
    playbook = PlayBook(
        playbook=playbook_file,
        inventory=inventory,
        remote_user=remote_user,
        remote_pass=remote_pass,
        transport=transport,
        extra_vars=extra_vars,
        only_tags=only_tags,
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        stats=stats
    )

    provision_success = False
    try:
        start = datetime.now()
        playbook.run()

        hosts = sorted(playbook.stats.processed.keys())
        print callbacks.banner("PLAY RECAP")
        playbook_cb.on_stats(playbook.stats)
        for h in hosts:
            t = playbook.stats.summarize(h)
            print "%s : %s %s %s %s\n" % (
                _hostcolor(h, t),
                _colorize('ok', t['ok'], 'green'),
                _colorize('changed', t['changed'], 'yellow'),
                _colorize('unreachable', t['unreachable'], 'red'),
                _colorize('failed', t['failures'], 'red'))
            if t['unreachable'] == 0 and t['failures'] == 0:
                provision_success = True

        print "Play run took {0} minutes\n".format((datetime.now() - start).seconds / 60)
    except errors.AnsibleError, e:
        print >> sys.stderr, "ERROR: %s" % e
    return provision_success


def _colorize(lead, num, color):
    """ Print 'lead' = 'num' in 'color' """
    if num != 0 and color is not None:
        return "%s%s%-15s" % (stringc(lead, color), stringc("=", color), stringc(str(num), color))
    else:
        return "%s=%-4s" % (lead, str(num))


def _hostcolor(host, stats, color=True):
    if color:
        if stats['failures'] != 0 or stats['unreachable'] != 0:
            return "%-37s" % stringc(host, 'red')
        elif stats['changed'] != 0:
            return "%-37s" % stringc(host, 'yellow')
        else:
            return "%-37s" % stringc(host, 'green')
    return "%-26s" % host


def run_modules(items):
    for item in items:
        print item['summary']
        success, result = run_module(item['module'])
        if not success:
            break


def run_module(runner):
    module_success = True
    module_result = ''
    results = runner.run()
    if len(results['dark']):
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
    tmp_inventory = '/tmp/prudentia-inventory'
    f = None
    try:
        f = open(tmp_inventory, 'w')
        f.write(box.inventory())
    except IOError, e:
        print e
    finally:
        f.close()
    return Inventory(tmp_inventory)


def local_inventory():
    return generate_inventory(Box('local', None, 'local', '127.0.0.1', use_prudentia_lib=True))
