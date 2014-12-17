import time
import subprocess
import os
import Queue
import atexit

from mininet.topo import Topo
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.net import Mininet


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
    

def num_flow_table_entries(switch_name):
    '''
    @param {String} switch_name --- Likely just "s1", "s2", etc.
    '''
    cmd_vec = ['ovs-ofctl','dump-flows',switch_name]

    (reading_pipe,writing_pipe) = os.pipe()
    reading_pipe = os.fdopen(reading_pipe,'r')
    writing_pipe = os.fdopen(writing_pipe,'w')

    subprocess.call(cmd_vec,stdout=writing_pipe)
    writing_pipe.flush()
    writing_pipe.close()

    # note starting from -1 here because must handle header returend
    # as part of dump-flows command
    num_entries = -1
    for line in reading_pipe:
        num_entries += 1

    reading_pipe.close()
    writing_pipe.close()
    
    return num_entries

