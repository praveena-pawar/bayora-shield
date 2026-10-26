#!/bin/sh
set -eu

# Block Red Team's dedicated network from reaching Blue Team.
if ! iptables -C DOCKER-USER \
    -s 172.23.0.0/16 \
    -d 172.26.0.0/16 \
    -p tcp --dport 8003 -j DROP 2>/dev/null; then
    iptables -I DOCKER-USER 1 \
        -s 172.23.0.0/16 \
        -d 172.26.0.0/16 \
        -p tcp --dport 8003 -j DROP
fi

# Block Red Team's integration-network IP from reaching Blue Team.
# Keep API traffic permitted: API uses 172.25.0.3.
if ! iptables -C DOCKER-USER \
    -s 172.25.0.2/32 \
    -d 172.26.0.2/32 \
    -p tcp --dport 8003 -j DROP 2>/dev/null; then
    iptables -I DOCKER-USER 1 \
        -s 172.25.0.2/32 \
        -d 172.26.0.2/32 \
        -p tcp --dport 8003 -j DROP
fi

echo "Red Team -> Blue Team firewall rules applied."
iptables -L DOCKER-USER -n -v --line-numbers