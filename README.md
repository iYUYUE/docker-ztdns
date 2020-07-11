# ztdns
## DNS Server Config
### Installing Prerequisites
```
apt install resolvconf dnsmasq
```
### Download the code
```
cd /var/lib/ && git clone https://github.com/iYUYUE/ztdns.git
chmod +x /var/lib/ztdns/update.sh
```
### Edit /etc/dnsmasq.conf
```
bind-dynamic
domain=example.com
domain-needed
bogus-priv
all-servers
no-negcache
server=8.8.8.8
server=8.8.4.4
addn-hosts=/etc/zerotier_hosts
```
### Add /var/lib/ztdns/zerotier.ini
```
# ZeroTier external inventory script settings

[zerotier]

# URL to the ZeroTier controller
controller = https://my.zerotier.com

# ZeroTier network ID to list hosts from
network = xxxxxxxxxxxxxxvv

# Access token to a user that has read privileges on that network
token = xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Include offline hosts in inventory
include_offline = true

domain = example.com

hosts = /etc/zerotier_hosts

```
### Test the code
```
/var/lib/ztdns/update.sh
```
On Ubuntu 18.04 or above, you may need to rm /etc/dnsmasq.d/lxd to make ``bind-dynamic`` work.

### Add a crontab task
```
* * * * *	/var/lib/ztdns/update.sh
```
## DNS Client Config
### Installing Prerequisites
```
apt install resolvconf dnsmasq
```
### Edit /etc/dnsmasq.conf
```
domain=example.com
domain-needed
bogus-priv
all-servers
no-negcache

server=/example.com/192.168.0.1
server=/example.com/192.168.0.2

server=/168.192.in-addr.arpa/192.168.0.1
server=/168.192.in-addr.arpa/192.168.0.2
```
