#!/bin/bash

# Clean up previous Mininet state
sudo mn -c

# Start main.py in the background
echo "B00937817" | sudo -S python3 /users/grad/etti/pinet/stream2gym/main.py /users/grad/etti/pinet/stream2gym/use-cases/disconnection/military-coordination/input.graphml --time 10 &

# Wait briefly for processes to start
sleep 1

echo "monitoring started"
sudo touch /users/grad/etti/pinet/stream2gym/logs/metrics.log
# Start monitoring script
sudo pidstat -u -r -p "$(pgrep -f 'python3 /users/grad/etti/pinet/stream2gym/main.py')" 1 100 > /users/grad/etti/pinet/stream2gym/logs/metrics.log

echo "monitoring ended"