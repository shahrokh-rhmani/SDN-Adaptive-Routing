# 1. ssh (Enable SSH keepalive to prevent automatic disconnection during idle sessions)

```
sudo nano /etc/ssh/sshd_config
```
```
ClientAliveInterval 120      
ClientAliveCountMax 5       
```
```
sudo service ssh restart
```

# 2. install python 3.9 for pox

### 1. 

```
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.9 python3.9-dev python3.9-venv
python3.9 --version
```

### 2. 
```
mkdir SDN-Adaptive-Routing
```
```
cd SDN-Adaptive-Routing
```

```
python3.9 -m venv env
source env/bin/activate
```

# 3. install mininet

```
sudo apt install mininet git
```
```
mn --version
```
```
pip install networkx
```

# 4. install pox

```
git clone https://github.com/noxrepo/pox.git
```

# 5. requirements.txt:
```
touch requirements.txt
```
```
pip freeze > requirements.txt
```
```
cat requirements.txt
```


