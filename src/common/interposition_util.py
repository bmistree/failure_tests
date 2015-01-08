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

FUZZER_LISTENING_PORT = 29599
FUZZER_LISTENING_ADDR = HostPortPair('0.0.0.0',FUZZER_LISTENING_PORT)
CONTROLLER_CONNECT_TO_ADDR = HostPortPair('127.0.0.1',6633)

def start_sdn_fuzzer_pass_through_in_thread():
    _thread_starter(ReorderType.WRITE_THROUGH)

    
FLOWMOD_TIMEOUT_SECONDS=3.0
    
def start_sdn_fuzzer_in_thread():
    _thread_starter(
        ReorderType.TIMED_REVERSE,
        json.dumps({'timeout_seconds':FLOWMOD_TIMEOUT_SECONDS}))


FAILURE_PROBABILITY = .2
# FAILURE_PROBABILITY = .0
def start_sdn_fuzzer_error_in_thread():
    _thread_starter(
        ReorderType.ERROR,
        json.dumps({'failure_probability':FAILURE_PROBABILITY}))

    
def _thread_starter(reorder_type,additional_args=None):
    t = threading.Thread(
        target=_thread_sdn_fuzzer,args=(reorder_type,additional_args))
    t.setDaemon(True)
    t.start()
    # wait some time until it's started
    time.sleep(5)
    


def _thread_sdn_fuzzer(reorder_type,additional_args):
    '''
    @param {string} reorder_type: One of the enumerated values from
    ReorderType.*

    @param {string or None} additional_args to send to interposition
    framework.
    '''
    interpose.run(
        reorder_type, FUZZER_LISTENING_ADDR,
        CONTROLLER_CONNECT_TO_ADDR, additional_args)

