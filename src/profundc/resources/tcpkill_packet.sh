#!/usr/bin/env bash
# tcpkill_one_packet.sh
# Usage: tcpkill_packet.sh <HEARTHSTONE_PID> <INTERFACE> <SERVER_IP>

PID="$1"
IFACE="$2"
SERVER_IP="$3"

echo "Running tcpkill under root..."

# Run tcpkill in the net namespace of the Hearthstone process.
nsenter --net="/proc/$PID/ns/net" tcpkill -i "$IFACE" host "$SERVER_IP" 2>&1 | \
while read -r line; do
  echo "$line"
  # When a line with '>' is detected, kill tcpkill.
  if [[ "$line" == *">"* ]]; then
    echo "Detected packet. Killing tcpkill now..."
    pkill -P $$ tcpkill || killall tcpkill
    break
  fi
done

echo "tcpkill_packet.sh finished."
