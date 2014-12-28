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
