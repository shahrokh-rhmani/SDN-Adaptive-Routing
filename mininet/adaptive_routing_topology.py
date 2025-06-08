from mininet.topo import Topo

class AdaptiveTopo(Topo):
    def __init__(self):
        super(AdaptiveTopo, self).__init__()
        s1,s2,s3 = (self.addSwitch(n) for n in ('s1','s2','s3'))
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')

        self.addLink(h1, s1, port1=1, port2=1)
        self.addLink(h2, s2, port1=1, port2=1)
        self.addLink(h3, s3, port1=1, port2=1)

        self.addLink(s1, s2, port1=2, port2=2)
        self.addLink(s2, s3, port1=3, port2=2)
        self.addLink(s3, s1, port1=3, port2=3)

topos = {'adaptive': (lambda: AdaptiveTopo())}
