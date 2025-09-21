# 1. clone project
```
git clone https://github.com/shahrokh-rhmani/SDN-Adaptive-Routing.git
```
```
cd SDN-Adaptive-Routing/
```

# 2. (terminal 1)
```
python3.9 -m venv env
```
```
source env/bin/activate
``` 
```
pip install -r requirements.txt
```

# 3. (terminal 1) run controller pox:
```
./pox/pox.py log.level --DEBUG  forwarding.adaptive_routing
```

# 4. (terminal 2) run mininet:
```
source env/bin/activate
```  

# 5. test network

### 1. Test connectivity between all hosts in the network
```
pingall
```
### 2. Test connectivity between two specific hosts
```
h1 ping h2
```
### 3. Display all flow rules installed on switches
```
dpctl dump-flows
```
### 4. Display OpenFlow switch information
```
sh ovs-ofctl show s1
```

# 6. Cleaning Mininet topologies and Checking and Freeing Port 6633 for pox
### 1. for port pox (terminal 1)
```
sudo lsof -i :6633
sudo kill -9 <PID>
```
### 2. for minient (terminal 2), Cleaning up previous Mininet topologies
```
exit
```
```
sudo mn -c 
```