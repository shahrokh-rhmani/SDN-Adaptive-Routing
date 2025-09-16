"""
AdaptiveRouting - POX SDN Controller (compatible with POX 0.7.0 gar)
  * Topology discovery: openflow.discovery
  * Shortest path: NetworkX
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
import networkx as nx

log = core.getLogger()


class AdaptiveRouting (object):
    def __init__(self):
        # Register for OpenFlow events
        core.openflow.addListeners(self)

        # Activate Discovery module internally to avoid extra arguments
        import pox.openflow.discovery
        pox.openflow.discovery.launch()
        core.openflow_discovery.addListeners(self)

        # Data structures for network state
        self.topology    = {}   # {dpid: {nbr_dpid: out_port}} - switch connectivity
        self.mac_to_port = {}   # {dpid: {mac: port}} - MAC learning table per switch
        self.hosts       = {}   # {IPAddr: (dpid, mac)} - Host IP to switch and MAC mapping
        self.graph       = nx.Graph()  # Network graph for path calculation

    # ───────── Switch connection handler ─────────
    def _handle_ConnectionUp(self, ev):
        # Called when a switch connects to the controller
        dpid = ev.dpid
        log.info("🔌 Switch %s connected", dpidToStr(dpid))
        # Initialize data structures for the new switch
        self.topology[dpid]    = {}
        self.mac_to_port[dpid] = {}

    # ───────── Link event handler (LLDP) ─────────
    def _handle_LinkEvent(self, ev):
        # Handle link discovery events from LLDP
        l = ev.link                # (dpid1,port1) ↔ (dpid2,port2)
        s1,p1,s2,p2 = l.dpid1, l.port1, l.dpid2, l.port2

        if ev.added:
            # Add link to topology and graph
            self.topology.setdefault(s1, {})[s2] = p1
            self.topology.setdefault(s2, {})[s1] = p2
            self.graph.add_edge(s1, s2)
            log.info("➕ %s:%d ↔ %s:%d", dpidToStr(s1),p1, dpidToStr(s2),p2)

        if ev.removed:
            # Remove link from topology and graph
            self.topology.get(s1, {}).pop(s2, None)
            self.topology.get(s2, {}).pop(s1, None)
            if self.graph.has_edge(s1, s2):
                self.graph.remove_edge(s1, s2)
            log.info("➖ %s:%d ↔ %s:%d", dpidToStr(s1),p1, dpidToStr(s2),p2)

    # ───────── Packet-In event handler ─────────
    def _handle_PacketIn(self, ev):
        # Main packet processing function
        pkt, dpid, in_p = ev.parsed, ev.dpid, ev.port

        # Learn MAC address to port mapping
        self.mac_to_port.setdefault(dpid, {}).setdefault(pkt.src, in_p)

        # Learn host IP to switch and MAC mapping
        if pkt.type == pkt.IP_TYPE:
            self.hosts[pkt.payload.srcip] = (dpid, pkt.src)

        # ARP processing
        if pkt.type == pkt.ARP_TYPE:
            self._handle_ARP(ev)
            return

        # IPv4 routing
        if pkt.type == pkt.IP_TYPE:
            ip = pkt.payload
            dst_ip = ip.dstip

            # Flood if destination host unknown
            if dst_ip not in self.hosts:
                self._flood(ev); return

            dst_dpid, dst_mac = self.hosts[dst_ip]

            if dpid == dst_dpid:                       # Same switch forwarding
                out = self.mac_to_port[dpid].get(dst_mac)
                self._unicast(dpid, out, pkt) if out else self._flood(ev)
            else:
                # Calculate and install path for inter-switch routing
                path = self._shortest(dpid, dst_dpid)
                if path:
                    log.debug("🛣 %s → %s : %s",
                              dpidToStr(dpid), dpidToStr(dst_dpid),
                              " → ".join(dpidToStr(sw) for sw in path))
                    self._install_path(path, pkt.src, dst_mac,
                                       ip.srcip, dst_ip)
                else:
                    self._flood(ev)
        else:
            # Flood non-IP packets
            self._flood(ev)

    # ───────── ARP handler ─────────
    def _handle_ARP(self, ev):
        # Process ARP packets
        pkt, arp, dpid = ev.parsed, ev.parsed.payload, ev.dpid

        if arp.opcode == arp.REQUEST:
            # Flood ARP requests if destination unknown
            self._flood(ev)

        elif arp.opcode == arp.REPLY:
            # Learn from ARP reply and forward to requester
            self.hosts[arp.protosrc] = (dpid, pkt.src)
            out = self.mac_to_port[dpid].get(arp.hwdst)
            self._unicast(dpid, out, pkt) if out else self._flood(ev)

    # ───────── Path calculation utilities ─────────
    def _shortest(self, s, d):
        # Calculate shortest path using NetworkX
        try:    return nx.shortest_path(self.graph, s, d)
        except: return None

    def _install_path(self, path, src_mac, dst_mac, src_ip, dst_ip):
        # Install flow rules along the calculated path
        for i, sw in enumerate(path):
            if i < len(path)-1:   next_sw = path[i+1]; out = self.topology[sw][next_sw]
            else:                 out = self.mac_to_port[sw][dst_mac]

            # Install forward flow (source to destination)
            fm = of.ofp_flow_mod()
            fm.match = of.ofp_match(dl_type=0x0800, nw_src=src_ip, nw_dst=dst_ip)
            fm.actions.append(of.ofp_action_output(port=out))
            core.openflow.sendToDPID(sw, fm)

            # Install reverse flow (destination to source)
            fm_b = of.ofp_flow_mod()
            fm_b.match = of.ofp_match(dl_type=0x0800, nw_src=dst_ip, nw_dst=src_ip)
            out_b = self.topology[sw][path[i-1]] if i else self.mac_to_port[sw][src_mac]
            fm_b.actions.append(of.ofp_action_output(port=out_b))
            core.openflow.sendToDPID(sw, fm_b)

    # ───────── Packet forwarding helpers ─────────
    def _flood(self, ev):
        # Flood packet to all ports (except input port)
        ev.connection.send(of.ofp_packet_out(
            data=ev.ofp, in_port=ev.port,
            actions=[of.ofp_action_output(port=of.OFPP_FLOOD)]))

    def _unicast(self, dpid, port, pkt):
        # Send packet to specific port
        if port is None: return self._flood(pkt)   # Fallback to flooding
        core.openflow.sendToDPID(dpid, of.ofp_packet_out(
            data=pkt.pack(), actions=[of.ofp_action_output(port=port)]))

# ───────── Module launcher ─────────
def launch():
    # Register the AdaptiveRouting component with POX core
    core.registerNew(AdaptiveRouting)
