#!/usr/bin/python
import signal
import time
import subprocess
from multiprocessing import Queue, Process

import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

DEPS_PATH = os.path.abspath(os.path.join(CURRENT_DIR,'..','..','deps'))
PYRETIC_PATH = os.path.join(DEPS_PATH,'pyretic')
POX_EXEC = os.path.join(DEPS_PATH,'pox','pox.py')

sys.path.append(PYRETIC_PATH)

from pyretic.core.runtime import Runtime
from pyretic.backend.backend import Backend

import reorder_lib
from pyretic.lib.corelib import *
from pyretic.lib.std import *

of_client = None
mininet = None

def signal_handler(sig, frame):
    print '\n----starting pyretic shutdown------'
    print 'attempting to kill of_client'
    of_client.kill()
    os.kill(mininet.pid,signal.SIGTERM)
    print 'pyretic.py done'
    sys.exit(0)


SINGLETON_REORDER_LIB = reorder_lib.ReorderLib()
def reorder_lib_main ():
    return SINGLETON_REORDER_LIB >> flood()

    
def main():
    global of_client,mininet
    mode = 'proactive1'
    logging_verbosity = 'low'
    path_main = None
    kwargs = {}
    
    # Set default handler.
    runtime = Runtime(
        Backend(),reorder_lib_main,path_main,kwargs,mode,logging_verbosity)

    # start mininet
    print '\nStarting mininet\n'
    env = os.environ.copy()
    env['HOME'] = DEPS_PATH
    cmd_vec = ['bash',os.path.join(PYRETIC_PATH,'mininet.sh')]
    mininet = subprocess.Popen(
        cmd_vec,stdout=sys.stdout,stderr=subprocess.STDOUT,
        env=env)

    # pause while mininet is getting set up.
    time.sleep(1)

    print '\nStarting mininet\n'
    # start pyretic
    python=sys.executable
    cmd_vec = [python, os.path.abspath(POX_EXEC), 'of_client.pox_client']
    env['PYTHONPATH'] = PYRETIC_PATH
    of_client = subprocess.Popen(
        cmd_vec,stdout=sys.stdout,stderr=subprocess.STDOUT,
        env=env)
    
    signal.signal(signal.SIGINT, signal_handler)

    time.sleep(3)

    # Update policies on switches.
    print '\nUpdating policies\n'
    SINGLETON_REORDER_LIB.change_policies()
    

    
    signal.pause()

if __name__ == '__main__':
    main()
