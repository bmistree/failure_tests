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
INTERPOSE_DIR = os.path.join(
    FILE_DIR,'..','..','deps','sdn_fuzz','bin')

# common imports
sys.path.append(os.path.join(FILE_DIR,'..','common'))
import mn_util
from interposition_util import (
    start_sdn_fuzzer_in_thread,FUZZER_LISTENING_PORT,
    FLOWMOD_TIMEOUT_SECONDS, start_sdn_fuzzer_pass_through_in_thread)

# pyretic imports
sys.path.append(PYRETIC_PATH)
from pyretic.core.runtime import Runtime
from pyretic.backend.backend import Backend
from pyretic.lib.corelib import *
from pyretic.lib.std import *

import reorder_lib


of_client = None
mininet = None

def signal_handler(sig, frame):
    print '[LOG] Starting shutdown'
    of_client.kill()
    os.kill(mininet.pid,signal.SIGTERM)
    print '[LOG] Shutdown complete'
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
        os.path.join(MININET_PATH,'extra-topos.py'),
        ('--controller=remote,port=%i' % FUZZER_LISTENING_PORT)]

    mininet = subprocess.Popen(
        cmd_vec,stdout=dev_null_fd,stderr=subprocess.STDOUT,
        env=env)
    

def main():
    mode = 'proactive1'
    logging_verbosity = 'low'
    path_main = None
    kwargs = {}
    
    # Set default handler.
    runtime = Runtime(
        Backend(),reorder_lib_main,path_main,kwargs,mode,logging_verbosity)

    # start pyretic
    print '[LOG] Starting pyretic'
    python=sys.executable
    cmd_vec = [python, os.path.abspath(POX_EXEC), 'of_client.pox_client']
    env = os.environ.copy()
    env['PYTHONPATH'] = PYRETIC_PATH
    global of_client
    of_client = subprocess.Popen(
        cmd_vec,stdout=sys.stdout,stderr=subprocess.STDOUT,
        env=env)
    time.sleep(FLOWMOD_TIMEOUT_SECONDS*3)

    # start sdn_fuzzer
    print '[LOG] Starting sdn fuzzer'
    start_sdn_fuzzer_in_thread()
    # start_sdn_fuzzer_pass_through_in_thread()
    time.sleep(FLOWMOD_TIMEOUT_SECONDS)
    
    # start mininet
    print '[LOG] Starting mininet'
    start_mininet()
    time.sleep(FLOWMOD_TIMEOUT_SECONDS*2)

    # listen for signal
    signal.signal(signal.SIGINT, signal_handler)

    # Update policies on switches.
    print '[LOG] Updating policies'
    SINGLETON_REORDER_LIB.change_policies()
    time.sleep(FLOWMOD_TIMEOUT_SECONDS*2)

    # Check number of flow table entries
    print '[LOG] Checking number of flow table entries'
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
