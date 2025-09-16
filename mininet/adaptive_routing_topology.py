# Import the Topo class from Mininet's topology module
from mininet.topo import Topo

# Define a custom topology class that inherits from Topo
class AdaptiveTopo(Topo):
    def __init__(self):
        # Call the parent class constructor
        super(AdaptiveTopo, self).__init__()
        
        # Create three switches using a generator expression
        # Each switch is assigned a name: s1, s2, s3
        s1,s2,s3 = (self.addSwitch(n) for n in ('s1','s2','s3'))
        
        # Create three hosts with specific IP addresses and MAC addresses
        # h1: IP 10.0.0.1/24, MAC 00:00:00:00:00:01
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        # h2: IP 10.0.0.2/24, MAC 00:00:00:00:00:02
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        # h3: IP 10.0.0.3/24, MAC 00:00:00:00:00:03
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')

        # Connect each host to a switch:
        # h1 connected to s1: host port 1, switch port 1
        self.addLink(h1, s1, port1=1, port2=1)
        # h2 connected to s2: host port 1, switch port 1
        self.addLink(h2, s2, port1=1, port2=1)
        # h3 connected to s3: host port 1, switch port 1
        self.addLink(h3, s3, port1=1, port2=1)

        # Create a triangular topology by connecting switches in a ring:
        # s1 connected to s2: s1 port 2, s2 port 2
        self.addLink(s1, s2, port1=2, port2=2)
        # s2 connected to s3: s2 port 3, s3 port 2
        self.addLink(s2, s3, port1=3, port2=2)
        # s3 connected to s1: s3 port 3, s1 port 3
        self.addLink(s3, s1, port1=3, port2=3)

# Register the topology with Mininet so it can be used with the mn command
# This creates a dictionary entry that maps the name 'adaptive' to our topology class
topos = {'adaptive': (lambda: AdaptiveTopo())}
