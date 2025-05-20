#!/bin/bash


# echo "pass" | sudo -S python3 /users/grad/etti/pinet/stream2gym/main.py /users/grad/etti/pinet/stream2gym/use-cases/disconnection/military-coordination/input.graphml --time 100 &
# main_pid=$!

echo "password" | sudo -S python3 run_experiments.py

# Wait briefly for processes to start
# sleep 1
# print log that this has started 
# echo "monitor_metrics.py started"
# Start monitoring script
# sudo python3 monitor_metrics.py --duration 100 --interval 1 --log-dir logs/output

# echo "monitor_metrics.py ended"
# sleep 3
# for i in $(seq 1 $(($1 + 1)))
# do
#     echo "Iteration $i"
#     sudo ip netns exec mn-h$i bash -c "python3 /users/grad/etti/pinet/stream2gym/metrics_script.py --host h$i" &
#     pids[$i]=$!
# done

# # Wait for the processes to complete or add your logic here
# for pid in ${pids[@]}; do
#     wait $pid
# done

# # Kill the background processes after completion
# for pid in ${pids[@]}; do
#     sudo kill $pid
# done
# done
