import sys
import logging
from src.cli import CLI

logging.basicConfig(format='%(asctime)s.%(msecs).03d [%(name)s] %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO)

sys.path.append('./src')
cli = CLI()
cli.setup()
cli.cmdloop()
