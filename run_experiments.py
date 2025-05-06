import pandas as pd
import subprocess
import time
import json
import os
import threading

# Configuration
TOPO_FILE = "/users/grad/etti/pinet/stream2gym/use-cases/disconnection/military-coordination/input.graphml"
SIM_TIME = 100
HOSTS = [f"h{i}" for i in range(1, 11)]
NAMESPACE_SETUP_DELAY = 20
PROGRESS_FILE = "progress.txt"

def get_last_completed_index():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return int(f.read().strip())
    return -1

def update_progress(run_index):
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(run_index))

# Load and filter schedule
df = pd.read_csv("schedule.csv")
last_completed_index = get_last_completed_index()
df_to_run = df[df["index"] > last_completed_index]

if df_to_run.empty:
    print("All simulation runs have been completed.")
    exit(0)

print(f"Processing runs from index {df_to_run['index'].min()} to {df_to_run['index'].max()}")
counter = 0

for _, row in df_to_run.iterrows():
    run_index = row["index"]
    print(f"\n=== Starting simulation run {run_index} ===")
    os.system("sudo rm ./status")
    
    # Prepare override properties
    producer_props = {
        "batchSize": row["producer->batch_size"],
        "linger": row["producer->linger_ms"],
        "compression": row["producer->compression_type"],
        "bufferMemory": row["producer->buffer_memory"],
    }
    consumer_props = {
        "fetchMaxWait": row["consumer->fetch_wait_max_ms"],
    }
    override_props = {
        "producer": producer_props,
        "consumer": consumer_props
    }
    override_json = json.dumps(override_props)

    # Clean up Mininet
    subprocess.run(["sudo", "mn", "-c"])
    print("Mininet cleaned up.")

    # Thread target: run main.py
    def run_main():
        print("Starting main.py...")
        main_cmd = [
            "python3", "/users/grad/etti/pinet/stream2gym/main.py",
            TOPO_FILE, "--time", str(SIM_TIME), "--override", override_json, "--index", str(run_index)
        ]
        proc = subprocess.Popen(main_cmd)
        proc.wait()
        thread_results['main_returncode'] = proc.returncode

    # Thread target: run metrics scripts
    def run_metrics():
        print(f"Waiting {NAMESPACE_SETUP_DELAY}s for namespaces to be ready...")
        time.sleep(NAMESPACE_SETUP_DELAY)
        print("Starting metrics scripts...")
        metric_pids = []
        for host in HOSTS:
            metric_cmd = [
                "sudo", "ip", "netns", "exec", f"mn-{host}", "bash", "-c",
                f"python3 /users/grad/etti/pinet/stream2gym/metrics_script.py --host {host} --index {run_index}"
            ]
            pid = subprocess.Popen(metric_cmd)
            metric_pids.append(pid)
        thread_results['metric_pids'] = metric_pids

    # Shared dictionary for results
    thread_results = {}

    # Create threads
    t_main = threading.Thread(target=run_main)
    t_metrics = threading.Thread(target=run_metrics)

    # Start threads
    t_main.start()
    t_metrics.start()

    # Wait for main.py to finish
    t_main.join()

    # Stop metrics processes
    if 'metric_pids' in thread_results:
        for pid in thread_results['metric_pids']:
            pid.terminate()

    if thread_results.get('main_returncode') == 0:
        update_progress(run_index)
        print(f"Run {run_index} completed successfully.")
    else:
        print(f"Run {run_index} failed with return code {thread_results.get('main_returncode')}")

    counter += 1
    if counter >= 10:
        print("Terminating after 10 runs for cleanup.")
        break

    time.sleep(60)

print("All simulation runs completed.")
