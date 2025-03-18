#!/bin/bash

# Clean up previous Mininet state
# sudo mn -c

# Start main.py in the background
echo "B00937817" | sudo -S python3 /users/grad/etti/pinet/stream2gym/main.py /users/grad/etti/pinet/stream2gym/use-cases/disconnection/military-coordination/input.graphml --time 100

# Wait briefly for processes to start
# sleep 1
# print log that this has started 
# echo "monitor_metrics.py started"
# Start monitoring script
# sudo python3 monitor_metrics.py --duration 100 --interval 1 --log-dir logs/output

# echo "monitor_metrics.py ended"