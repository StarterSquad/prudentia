import os
import sys
import logging
from src.cli import CLI

# Change cwd in prudentia dir
os.chdir(os.path.dirname(os.path.realpath(__file__)))

logging.basicConfig(format='%(asctime)s.%(msecs).03d [%(name)s] %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO)

sys.path.append('./src')
cli = CLI()
cli.setup()
cli.cmdloop()
