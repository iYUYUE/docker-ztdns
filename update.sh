#!/bin/bash
set -e
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

echo "Retrieving Network Inventory..."
python3 "$parent_path/zerotier.py" --refresh

echo "Restarting dnsmasq service..."
if hash systemctl 2>/dev/null; then
  systemctl restart dnsmasq
elif hash service 2>/dev/null; then
  service dnsmasq restart
else
  echo "Now please restart dnsmasq since I don't know how to do it."
fi
