__version__ = '0.8.1'
__author__ = 'Tiziano Perrucci'

import readline
import atexit
import os

if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")


historyPath = os.path.join(os.environ['PRUDENTIA_USER_DIR'], '.history.txt')


def save_history(p=historyPath):
    import readline
    readline.write_history_file(p)


if os.path.exists(historyPath):
    try:
        readline.read_history_file(historyPath)
    except:
        pass

atexit.register(save_history)
del os, atexit, readline, save_history, historyPath
