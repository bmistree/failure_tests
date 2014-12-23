#!/usr/bin/env python

import time
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
from floodlight_util import start_floodlight,add_flowmod


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

def _thread_sdn_fuzzer():
    interpose.run(
        ReorderType.WRITE_THROUGH, FUZZER_LISTENING_ADDR,
        CONTROLLER_CONNECT_TO_ADDR,'')


def run():
    print '[LOG] Starting floodlight'
    start_floodlight()
    time.sleep(5)
    print '[LOG] Starting sdn fuzzer'
    start_sdn_fuzzer_in_thread()
    print '[LOG] Starting mininet'
    time.sleep(20)
    switch_name = start_mininet(1,FUZZER_LISTENING_PORT)[0]
    print '[LOG] Sending static entries'
    add_flowmod()
    time.sleep(5)
    
    num_entries = num_flow_table_entries(switch_name)
    print '\nNumber of flow table entries: %i\n' % num_entries

    time.sleep(20)
    


if __name__ == '__main__':
    run()
