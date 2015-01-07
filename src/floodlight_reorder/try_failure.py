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

from mininet_util import start_mininet,num_flow_table_entries
from floodlight_util import start_floodlight,add_flowmod,remove_flowmod

# import common
COMMON_DIR = os.path.join(FILE_DIR,'..','common')
sys.path.append(COMMON_DIR)
from interposition_util import (
    start_sdn_fuzzer_error_in_thread,FUZZER_LISTENING_PORT,
    start_sdn_fuzzer_pass_through_in_thread)

NUM_ENTRIES_TO_ADD = 50

'''
  1) Starts floodlight.
  2) Starts sdn_fuzzer.
  3) Start mininet, pointing it at fuzzer.
  4) Send NUM_ENTRIES_TO_ADD sets of static entries.
  5) Read number of entries and compare against expected.
'''

def run():
    print '[LOG] Starting floodlight'
    start_floodlight()
    time.sleep(5)
    print '[LOG] Starting sdn fuzzer'
    start_sdn_fuzzer_error_in_thread()
    print '[LOG] Starting mininet'
    time.sleep(10)
    switch_name = start_mininet(1,FUZZER_LISTENING_PORT)[0]
    print '[LOG] Sending static add/remove entries'

    for i in range(0,NUM_ENTRIES_TO_ADD):
        add_flowmod(i)

    time.sleep(3)
    num_entries = num_flow_table_entries(switch_name)

    print '\n\n'
    if num_entries == NUM_ENTRIES_TO_ADD:
        print 'Floodlight PASSED rejection test'
    else:
        print (
            'Floodlight FAILED rejection test; num entries: %i; num expected entries %i'
            % (num_entries,NUM_ENTRIES_TO_ADD))
    print '\n\n'


if __name__ == '__main__':
    run()
