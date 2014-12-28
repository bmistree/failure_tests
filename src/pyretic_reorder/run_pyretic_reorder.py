#!/usr/bin/python
import signal
import time
import subprocess
from multiprocessing import Queue, Process

import sys
import os
FILE_DIR = os.path.dirname(os.path.abspath(__file__))

DEPS_PATH = os.path.abspath(os.path.join(FILE_DIR,'..','..','deps'))
PYRETIC_PATH = os.path.join(DEPS_PATH,'pyretic')
MININET_PATH = os.path.join(PYRETIC_PATH,'mininet')
POX_EXEC = os.path.join(DEPS_PATH,'pox','pox.py')

sys.path.append(os.path.join(FILE_DIR,'..','common'))
sys.path.append(PYRETIC_PATH)

from pyretic.core.runtime import Runtime
from pyretic.backend.backend import Backend

import reorder_lib
from pyretic.lib.corelib import *
from pyretic.lib.std import *


import mn_util


of_client = None
mininet = None

def signal_handler(sig, frame):
    print '\n----starting pyretic shutdown------'
    print 'attempting to kill of_client and mininet'
    of_client.kill()
    os.kill(mininet.pid,signal.SIGTERM)
    print 'pyretic.py done'
    sys.exit(0)


SINGLETON_REORDER_LIB = reorder_lib.ReorderLib()
def reorder_lib_main ():
    return SINGLETON_REORDER_LIB >> flood()

def start_mininet():
    global mininet
    python=sys.executable
    env = os.environ.copy()
    env['HOME'] = DEPS_PATH

    # clear existing mininets
    with open(os.devnull,'wb') as dev_null_fd:
        cmd_vec = [python,os.path.join(MININET_PATH,'mn'),'-c']
        subprocess.call(
            cmd_vec,stdout=dev_null_fd,stderr=subprocess.STDOUT,
            env=env)

    # start mininet
    dev_null_fd = open(os.devnull,'wb')
    cmd_vec = [
        python,os.path.join(MININET_PATH,'mn'),'--custom',
        os.path.join(MININET_PATH,'extra-topos.py'),'--controller','remote']
    mininet = subprocess.Popen(
        cmd_vec,stdout=dev_null_fd,stderr=subprocess.STDOUT,
        env=env)


def main():
    global of_client
    mode = 'proactive1'
    logging_verbosity = 'low'
    path_main = None
    kwargs = {}
    
    # Set default handler.
    runtime = Runtime(
        Backend(),reorder_lib_main,path_main,kwargs,mode,logging_verbosity)

    # start mininet
    print '\nStarting mininet\n'
    start_mininet()

    # pause while mininet is getting set up.
    time.sleep(1)

    # start pyretic
    print '\nStarting pyretic\n'
    python=sys.executable
    cmd_vec = [python, os.path.abspath(POX_EXEC), 'of_client.pox_client']
    env = os.environ.copy()
    env['PYTHONPATH'] = PYRETIC_PATH
    of_client = subprocess.Popen(
        cmd_vec,stdout=sys.stdout,stderr=subprocess.STDOUT,
        env=env)
    
    signal.signal(signal.SIGINT, signal_handler)

    time.sleep(3)

    # Update policies on switches.
    print '\nUpdating policies\n'
    SINGLETON_REORDER_LIB.change_policies()
    
    time.sleep(3)

    # Check number of flow table entries
    print '\nChecking number of flow table entries\n'
    num_flow_table_entries = mn_util.num_flow_table_entries('s1')

    if num_flow_table_entries != 11:
        print (
            '\nREORDERING occurred; num entries %i\n' %
            num_flow_table_entries)
    else:
        print (
            '\nNo reordering occurred; num entries %i\n' %
            num_flow_table_entries)
    
    signal.pause()

if __name__ == '__main__':
    main()
