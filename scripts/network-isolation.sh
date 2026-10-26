#!/bin/sh
set -eu

# Block direct TCP access from the Red Team network to Blue Team.
if ! iptables -C DOCKER-USER -s 172.23.0.0/16 -d 172.26.0.0/16 -p tcp --dport 8003 -j DROP 2>/dev/null; then
    iptables -I DOCKER-USER 1 -s 172.23.0.0/16 -d 172.26.0.0/16 -p tcp --dport 8003 -j DROP
fi

echo "Red Team -> Blue Team firewall rule applied."
iptables -S DOCKER-USER
