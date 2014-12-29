import threading
import json
import time

import os
import sys
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
INTERPOSE_DIR = os.path.join(
    FILE_DIR,'..','..','deps','sdn_fuzz','bin')
sys.path.append(INTERPOSE_DIR)

import interpose
from interpose_arg_helper import ReorderType


class HostPortPair(object):
    def __init__(self,hostname,port):
        self.hostname = hostname
        self.port = port

FUZZER_LISTENING_PORT = 39589
FUZZER_LISTENING_ADDR = HostPortPair('0.0.0.0',FUZZER_LISTENING_PORT)
CONTROLLER_CONNECT_TO_ADDR = HostPortPair('127.0.0.1',6633)

def start_sdn_fuzzer_pass_through_in_thread():
    t = threading.Thread(
        target=_thread_sdn_fuzzer,args=(ReorderType.WRITE_THROUGH,))
    t.setDaemon(True)
    t.start()
    # wait some time until it's started
    time.sleep(5)

def start_sdn_fuzzer_in_thread():
    t = threading.Thread(
        target=_thread_sdn_fuzzer,args=(ReorderType.TIMED_REVERSE,))
    t.setDaemon(True)
    t.start()
    # wait some time until it's started
    time.sleep(5)

FLOWMOD_TIMEOUT_SECONDS=3.0

def _thread_sdn_fuzzer(reorder_type):
    '''
    One of the enumerated values from ReorderType.*
    '''
    interpose.run(
        reorder_type, FUZZER_LISTENING_ADDR,
        CONTROLLER_CONNECT_TO_ADDR,
        # used only for timed reverse.  but not bad to pass through
        # otherwise.
        json.dumps({'timeout_seconds':FLOWMOD_TIMEOUT_SECONDS}))
