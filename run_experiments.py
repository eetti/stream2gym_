import pandas as pd
import subprocess
import time
import json
import os

# Configuration
TOPO_FILE = "/users/grad/etti/pinet/stream2gym/use-cases/disconnection/military-coordination/input.graphml"
SIM_TIME = 100  # Simulation duration in seconds, adjust as needed
HOSTS = [f"h{i}" for i in range(1, 11)]  # 10 hosts: h1 to h10
NAMESPACE_SETUP_DELAY = 20  # Seconds to wait for namespaces to be created
PROGRESS_FILE = "progress.txt"  # File to track the last completed run

# Read the last completed index from progress.txt
def get_last_completed_index():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return int(f.read().strip())
    return -1  # If file doesn't exist, assume no runs completed

# Update the progress file with the current run index
def update_progress(run_index):
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(run_index))
        
# Read schedule-1.csv
df = pd.read_csv("schedule.csv")

# Get the last completed index
last_completed_index = get_last_completed_index()

# Filter DataFrame to include only unprocessed rows
df_to_run = df[df["index"] > last_completed_index]

if df_to_run.empty:
    print("All simulation runs have been completed.")
    exit(0)

print(f"Processing runs from index {df_to_run['index'].min()} to {df_to_run['index'].max()}")
counter = 0
for _, row in df_to_run.iterrows():
    print(f"Starting simulation run {row['index']}...")
    os.system("sudo rm ./status")
    run_index = row["index"]
    # Extract producer properties from the CSV row
    producer_props = {
        "batchSize": row["producer->batch_size"],
        "linger": row["producer->linger_ms"],
        "compression": row["producer->compression_type"],
        "bufferMemory": row["producer->buffer_memory"],
        # Add other producer properties if present in your CSV (e.g., "acks", "bufferMemory")
    }
    # Extract consumer properties if applicable
    consumer_props = {
        "fetchMaxWait": row["consumer->fetch_wait_max_ms"],
    }
    override_props = {
        "producer": producer_props,
        "consumer": consumer_props
    }
    override_json = json.dumps(override_props)

    # Clean up previous Mininet state
    subprocess.run(["sudo", "mn", "-c"])

    # Start main.py with override properties
    main_cmd = [
        "python3", "/users/grad/etti/pinet/stream2gym/main.py",
        TOPO_FILE, "--time", str(SIM_TIME), "--override", override_json, "--index", str(run_index)
    ]
    main_pid = subprocess.Popen(main_cmd)
    # update_progress(run_index) #wwriting the progress to the file
    
    print(f"Waiting {NAMESPACE_SETUP_DELAY} seconds for namespaces to be set up...")
    time.sleep(NAMESPACE_SETUP_DELAY)

    # Start metrics_script.py for each host with the run_index
    metric_pids = []
    for host in HOSTS:
        metric_cmd = [
            "sudo", "ip", "netns", "exec", f"mn-{host}", "bash", "-c",
            f"python3 /users/grad/etti/pinet/stream2gym/metrics_script.py --host {host} --index {run_index}"
        ]
        metric_pid = subprocess.Popen(metric_cmd)
        metric_pids.append(metric_pid)

    # Wait for main.py to finish
    main_pid.wait()
    
    # Check if the simulation was successful
    if main_pid.returncode == 0:
        # Update progress only if the run completed successfully
        update_progress(run_index)
        print(f"Run {run_index} completed successfully.")
    else:
        print(f"Run {run_index} failed with return code {main_pid.returncode}")
        # Optionally, break or handle the failure differently
        # For now, we'll continue to the next run

    # Terminate metrics collection processes
    for pid in metric_pids:
        pid.terminate()
    counter = counter + 1
    if counter >= 10:
        print("Terminating after 10 runs for cleanup.")
        break
    # Brief pause for cleanup
    time.sleep(90)

print("All simulation runs completed.")