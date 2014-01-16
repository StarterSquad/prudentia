import sys
import logging
from src.cli import CLI

logging.basicConfig(
    format='%(asctime)s.%(msecs).03d [%(name)s] %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    level=logging.WARNING
)

cli = CLI()

if len(sys.argv) > 1:
    env = sys.argv[1]
    if not cli.do_use(env):
        cli.cmdloop()
else:
    cli.cmdloop()

sys.exit(0)
