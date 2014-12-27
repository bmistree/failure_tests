#!/usr/bin/python
import signal
import subprocess
from multiprocessing import Queue, Process

import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PYRETIC_PATH = os.path.join(CURRENT_DIR,'..','..','deps','pyretic')
POX_EXEC = os.path.join(CURRENT_DIR,'..','..','deps','pox','pox.py')

sys.path.append(PYRETIC_PATH)

from pyretic.core.runtime import Runtime
from pyretic.backend.backend import Backend


import reorder_lib

of_client = None

def signal_handler(signal, frame):
    print '\n----starting pyretic shutdown------'
    print 'attempting to kill of_client'
    of_client.kill()
    print 'pyretic.py done'
    sys.exit(0)


def main():
    global of_client
    mode = 'proactive1'
    logging_verbosity = 'low'
    path_main = None
    kwargs = {}
    
    # Set default handler.
    runtime = Runtime(
        Backend(),reorder_lib.main,path_main,kwargs,mode,logging_verbosity)

    python=sys.executable
    cmd_vec = [python, os.path.abspath(POX_EXEC), 'of_client.pox_client']

    env = os.environ.copy()
    env['PYTHONPATH'] = PYRETIC_PATH
    
    of_client = subprocess.Popen(
        cmd_vec,stdout=sys.stdout,stderr=subprocess.STDOUT,
        env=env)
        

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()

if __name__ == '__main__':
    main()
