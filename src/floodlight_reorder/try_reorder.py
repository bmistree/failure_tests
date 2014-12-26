#!/usr/bin/env python

import time
import json
import threading
import os
import sys
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
INTERPOSE_DIR = os.path.join(
    FILE_DIR,'..','..','deps','sdn_fuzz','bin')
sys.path.append(INTERPOSE_DIR)

import interpose
from interpose_arg_helper import ReorderType

from mininet_util import start_mininet,num_flow_table_entries
from floodlight_util import start_floodlight,add_flowmod,remove_flowmod


'''
  1) Starts floodlight.
  2) Starts sdn_fuzzer.
  3) Start mininet, pointing it at fuzzer.
  4) Send static entries.
  5) Read number of entries and compare against expected.
'''

class HostPortPair(object):
    def __init__(self,hostname,port):
        self.hostname = hostname
        self.port = port

FUZZER_LISTENING_PORT = 18589
FUZZER_LISTENING_ADDR = HostPortPair('0.0.0.0',FUZZER_LISTENING_PORT)
CONTROLLER_CONNECT_TO_ADDR = HostPortPair('127.0.0.1',6633)

def start_sdn_fuzzer_in_thread():
    t = threading.Thread(target=_thread_sdn_fuzzer)
    t.setDaemon(True)
    t.start()
    # wait some time until it's started
    time.sleep(5)

FLOWMOD_TIMEOUT_SECONDS=3.0

def _thread_sdn_fuzzer():
    interpose.run(
        ReorderType.TIMED_REVERSE, FUZZER_LISTENING_ADDR,
        CONTROLLER_CONNECT_TO_ADDR,
        json.dumps({'timeout_seconds':FLOWMOD_TIMEOUT_SECONDS}))

    
def run():
    print '[LOG] Starting floodlight'
    start_floodlight()
    time.sleep(5)
    print '[LOG] Starting sdn fuzzer'
    start_sdn_fuzzer_in_thread()
    print '[LOG] Starting mininet'
    time.sleep(20)
    switch_name = start_mininet(1,FUZZER_LISTENING_PORT)[0]
    print '[LOG] Sending static add entry'
    add_flowmod()
    time.sleep(FLOWMOD_TIMEOUT_SECONDS/5.)
    print '[LOG] Sending static remove entry'
    remove_flowmod()
    time.sleep(FLOWMOD_TIMEOUT_SECONDS*3)
    num_entries = num_flow_table_entries(switch_name)

    print '\n\n'
    if num_entries == 0:
        print 'NO REORDERING'
    else:
        print 'REORDERING OCCURRED; num entries: %i' % num_entries
    print '\n\n'


if __name__ == '__main__':
    run()
