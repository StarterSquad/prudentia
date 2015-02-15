__version__ = '0.8.1'
__author__ = 'Tiziano Perrucci'


import readline

if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")
