import sys

import threading
import time

from pyretic.lib.corelib import *
from pyretic.lib.std import *


class ReorderLib(DynamicPolicy):

    def __init__(self):
        super(ReorderLib,self).__init__(true)

        
    def change_policies(self):
        time.sleep(1)
        self.first_call()
        time.sleep(1)
        self.second_call()

        
    def first_call(self):
        '''
        Add a policy to switches
        '''
        mac_add = '00:11:22:33:44:50'
        srcip_add = '10.1.1.1'
        add_match = match(srcmac=mac_add) & match(srcip=srcip_add)

        srcip_remove = '10.1.1.1'
        second_match = match(srcip=srcip_remove)

        self.policy = ~union([
                add_match >> second_match ])


    def second_call(self):
        '''
        Add a new policy to switches, which causes switches to issue a
        modify message of the original message.
        '''
        mac_add = '00:11:22:33:44:50'
        srcip_add = '10.1.1.1'
        add_match = match(srcmac=mac_add) & match(srcip=srcip_add)
        self.policy = ~union([add_match])
        
