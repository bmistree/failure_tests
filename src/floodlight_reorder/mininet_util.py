import time
import subprocess
import sys
import os
import Queue
import atexit

from mininet.topo import Topo
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.net import Mininet

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(FILE_DIR,'..','common'))
import mn_util

DEFAULT_CONTROLLER_PORT=6633

class FlatTopo(Topo):
    'N switches, no connections, no hosts'
    def __init__(self, switches=1, **opts):
        Topo.__init__(self, **opts)
        for i in range(switches):
            switch = self.addSwitch('s%d' % (i + 1))

def _switch_names(num_switches):
    '''
    @returns {list} --- Each element is a string containing a switch
    name.
    '''
    to_return = []
    for i in range(1, num_switches+1):
        to_return.append('s%d' % i)
    return to_return

mininet_to_kill_queue = Queue.Queue()

def start_mininet(num_switches,controller_port=DEFAULT_CONTROLLER_PORT):
    '''
    @returns {list} --- Each element is a string containing a switch
    name.
    '''
    # Run Mininet
    net = Mininet(
        topo=FlatTopo(switches=num_switches), build=False, switch=OVSSwitch)
    net.addController(
        RemoteController('c0', ip='127.0.0.1', port=controller_port))

    global mininet_to_kill_queue
    mininet_to_kill_queue.put(net)
    
    time.sleep(5)
    net.build()
    time.sleep(5)
    net.start()
    time.sleep(5)
    return _switch_names(num_switches)

@atexit.register
def cleanup_mininet():
    print '[Log] Cleaning stray mininets'
    global mininet_to_kill_queue
    while True:
        try:
            net_to_kill = mininet_to_kill_queue.get(False,1)
            net_to_kill.stop()
        except Queue.Empty:
            break

        
num_flow_table_entries = mn_util.num_flow_table_entries
