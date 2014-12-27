import sys
sys.path.append('../../../pox/pox/')

import threading
import time

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.modules.mac_learner import mac_learner

class ReorderLib(DynamicPolicy):

    def __init__(self):
        super(ReorderLib,self).__init__(true)
        t = threading.Thread(target=self.running_thread)
        t.setDaemon(True)
        t.start()
        
    def running_thread(self):
        time.sleep(5)
        self.first_call()
        time.sleep(5)
        self.second_call()

        
    def first_call(self):
        '''
        Add a policy to switches
        '''
        print '\nFirst call\n'

        import os
        print os.getcwd()
        print '\n'
        
        mac_add = '00:11:22:33:44:50'
        srcip_add = '10.1.1.1'
        add_match = match(srcmac=mac_add) & match(srcip=srcip_add)

        srcip_remove = '10.1.1.1'
        second_match = match(srcip=srcip_remove)

        self.policy = ~union([
                add_match >> second_match ])
        print self.policy

    def second_call(self):
        '''
        Add a new policy to switches, which causes switches to issue a
        modify message of the original message.
        '''
        print '\nSecond call\n'
        
        mac_add = '00:11:22:33:44:50'
        srcip_add = '10.1.1.1'
        add_match = match(srcmac=mac_add) & match(srcip=srcip_add)
        self.policy = ~union([add_match])


def main ():
    return ReorderLib() >> flood()
