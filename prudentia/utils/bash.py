import logging
import os
from subprocess import PIPE, Popen
from threading import Thread
import sys


class BashCmd(object):
    def __init__(self, *cmd_args):
        self.cmd_args = cmd_args
        self.env = os.environ.copy()
        self.cwd = os.getcwd()
        self.show_output = True
        self.output_stdout = []
        self.output_stderr = []
        self.ON_POSIX = 'posix' in sys.builtin_module_names

    def set_env_var(self, var, value):
        if value:
            self.env[var] = value

    def set_cwd(self, cwd):
        self.cwd = cwd

    def set_show_output(self, b):
        self.show_output = b

    def print_output(self, out, err):
        try:
            for line in iter(out.readline, b''):
                if self.show_output:
                    print line.strip()
                self.output_stdout.append(line)
            for line in iter(err.readline, b''):
                print "ERR - ", line.strip()
                self.output_stderr.append(line)
        finally:
            out.close()
            err.close()

    def execute(self):
        try:
            p = Popen(args=self.cmd_args, bufsize=1, stdout=PIPE, stderr=PIPE, close_fds=self.ON_POSIX, env=self.env,
                      cwd=self.cwd)
            t = Thread(target=self.print_output, args=(p.stdout, p.stderr))
            t.daemon = True # thread dies with the program
            t.start()
            p.wait()
            self.stdout = "".join(self.output_stdout)
            self.stderr = "".join(self.output_stderr)
            self.returncode = p.returncode
        except Exception as e:
            logging.exception('Command not executed.')
            print("ERROR - Problem running {0}: {1}".format(self.cmd_args, e))

    def __repr__(self):
        return "{0}" \
               "\nReturn code: {1}" \
               "\nStd Output: {2}" \
               "\nStd Error: {3}".format(self.cmd_args, self.returncode, self.stdout, self.stderr)

    def is_ok(self):
        if not self.returncode:
            return True
        else:
            return False

    def output(self):
        return self.stdout