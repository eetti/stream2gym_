#!/usr/bin/python3

import psutil
import time
import subprocess
import os
from datetime import datetime
import argparse

def get_pids(pattern):
    """Find PIDs of processes matching a pattern using pgrep."""
    try:
        result = subprocess.run(f"pgrep -f '{pattern}'", shell=True, capture_output=True, text=True)
        pids = result.stdout.strip().split("\n")
        return [int(pid) for pid in pids if pid]  # Convert to integers, filter empty strings
    except Exception as e:
        print(f"Error finding PIDs for {pattern}: {e}")
        return []

def collect_metrics(pids, log_dir, duration, interval=1):
    """Collect system metrics for given PIDs over a specified duration."""
    os.makedirs(log_dir, exist_ok=True)
    start_time = time.time()
    
    # Open log files for each process
    log_files = {}
    for pid in pids:
        log_file_path = f"{log_dir}/metrics_pid_{pid}.txt"
        try:
            # Ensure the file is created with sudo if necessary
            subprocess.run(f"sudo touch {log_file_path}", shell=True, check=True)
            log_files[pid] = open(log_file_path, "a")
        except subprocess.CalledProcessError as e:
            print(f"Error creating log file {log_file_path}: {e}")
    
    print(f"Monitoring PIDs: {pids} for {duration} seconds")
    while time.time() - start_time < duration:
        for pid in pids.copy():  # Use copy to allow removal during iteration
            try:
                print(f"Monitoring PID {pid}")
                process = psutil.Process(pid)
                cpu_percent = process.cpu_percent(interval=interval)  # Measures CPU over interval
                memory_info = process.memory_info()
                timestamp = datetime.now()
                log_files[pid].write(
                    f"{timestamp}, CPU: {cpu_percent}%, Memory: {memory_info.rss / 1024 / 1024} MB\n"
                )
                log_files[pid].flush()  # Ensure data is written immediately
            except psutil.NoSuchProcess:
                print(f"Process PID {pid} terminated")
                log_files[pid].close()
                # del log_files[pid]
                pids.remove(pid)
        
        time.sleep(interval)  # Wait for the next interval
    
    # Close all log files
    for f in log_files.values():
        f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor system metrics for Mininet processes.")
    parser.add_argument("--duration", type=int, default=30, help="Duration to monitor in seconds")
    parser.add_argument("--interval", type=float, default=1, help="Interval between measurements in seconds")
    parser.add_argument("--log-dir", type=str, default="logs/output", help="Directory to store metric logs")
    args = parser.parse_args()

    # Patterns to match your Mininet custom scripts
    process_patterns = [
        "python3 /users/grad/etti/pinet/stream2gym/main.py",           # Main Mininet script
        "kafka-server-start",        # Kafka brokers (adjust if different)
        "zookeeper-server-start"     # Zookeeper (adjust if different)
    ]

    # Collect all relevant PIDs
    all_pids = []
    for pattern in process_patterns:
        pids = get_pids(pattern)
        if pids:
            all_pids.extend(pids)
            print(f"Found PIDs for '{pattern}': {pids}")

    if not all_pids:
        print("No matching processes found. Ensure Mininet simulation is running.")
        exit(1)

    # Start monitoring
    collect_metrics(all_pids, args.log_dir, args.duration, args.interval)
    print(f"Metrics collection complete. Logs saved in {args.log_dir}")