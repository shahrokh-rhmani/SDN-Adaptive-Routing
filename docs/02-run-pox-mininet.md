# 1. virtual environment

```
source pox-env/bin/activate
```

```
cd pox
```


# 2. create file adaptive_routing.py

```
nano ~/pox/pox/forwarding/adaptive_routing.py
```

or

```
nano pox/forwarding/adaptive_routing.py
```

# 3. create file adaptive_routing_topology.py

```
nano ~/mininet/adaptive_routing_topology.py
```

# 4. (terminal 1) run controller pox

```
./pox.py log.level --DEBUG  forwarding.adaptive_routing
```

# 5. (terminal 1) run mininet 

```
sudo mn --custom adaptive_routing_topology.py --controller=remote,ip=127.0.0.1,port=6633 --topo=adaptive
```

# 6. test network

```
pingall
h1 ping h2
dpctl dump-flows
sh ovs-ofctl show s1
```

# 7. Cleaning Mininet topologies and Checking and Freeing Port 6633 for pox

for port pox
```
sudo lsof -i :6633
sudo kill -9 <PID>
```

for minient 
```
sudo mn -c  # Cleaning up previous Mininet topologies
```