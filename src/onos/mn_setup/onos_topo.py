from mininet.topo import Topo


class TwoHostsOneSwitchTopo(Topo):
    SWITCH_NAME = 's1'
    HOST1_NAME = 'h1'
    HOST2_NAME = 'h2'
    
    def __init__(self):
        '''
        h1 <---> s1 <---> h2
        '''
        self.addSwitch(TwoHostsOneSwitchTopo.SWITCH_NAME)
        self.addHost(TwoHostsOneSwitchTopo.HOST1_NAME,ip=None)
        self.addHost(TwoHostsOneSwitchTopo.HOST2_NAME,ip=None)

        # now actually connect hosts to switches
        self.addLink(TwoHostsOneSwitchTopo.SWITCH_NAME,
                     TwoHostsOneSwitchTopo.HOST1_NAME)
        self.addLink(TwoHostsOneSwitchTopo.SWITCH_NAME,
                     TwoHostsOneSwitchTopo.HOST2_NAME)
        

