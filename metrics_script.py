#!/usr/bin/python3

import subprocess
import argparse
import time
from jmxquery import JMXConnection, JMXQuery
import pandas as pd
import numpy as np
import json
import os

# Configuration
BASE_JMX_PORT = 9999
INTERVAL = 5

def get_jmx_metrics(host, port, run_index):
    host_id = int(host[1:])
    jmx_url = f"service:jmx:rmi:///jndi/rmi://10.0.0.{host_id}:{port}/jmxrmi"
    jmx = JMXConnection(jmx_url)
    
    with open('./meta/docker_kafka.json') as f:
        mbeans = json.load(f)
    _query_obj = [
        JMXQuery(mBeanName=mbean['ObjectName'], attribute=val['Attribute'],
                 value_type=val['Type'], metric_name=val['InstancePrefix'],
                 metric_labels={'type': val['Type']})
        for mbean in mbeans for val in mbean['Values']
    ]
    
    state_cols = pd.read_csv('./meta/kafka_state_meta.csv')['name'].tolist()
    csv_file = f'./metrics/states-{host}.csv'
    if not os.path.exists(csv_file):
        with open(csv_file, 'w') as f:
            f.write('run_index,timestamp,host,' + ','.join(state_cols) + '\n')
    
    observations = {}
    failures = 0
    stop = False
    while not stop:
        try:
            metrics = jmx.query(_query_obj)
            if metrics:
                # timestamp = time.time()
                # results = {'run_index': run_index, 'timestamp': timestamp, 'host': host}
                for mtr in metrics:
                    mtr_name = mtr.metric_name
                    mtr_val = mtr.value
                    mtr_type = mtr.metric_labels['type']
                    if mtr_name in ['last_gc_info', 'memory_heap_usage', 'memory_non_heap_usage']:
                        mtr_name = f'{mtr_name}_{mtr.attributeKey}'
                    if not mtr_val:
                        continue
                    if mtr_name not in observations:
                        observations[mtr_name] = [mtr_val] if mtr_type == 'gauge' else mtr_val
                    else:
                        if mtr_type == 'gauge':
                            observations[mtr_name].append(mtr_val)
                        elif mtr_type == 'counter':
                            observations[mtr_name] = mtr_val
                
                
        except Exception as e:
            print(f"Error querying JMX for {host}: {e}")
            failures += 1
            if failures >= 5:
                stop = True
        time.sleep(INTERVAL)
    # Write current metrics with run_index
    timestamp = time.time()
    results = {'run_index': run_index, 'timestamp': timestamp, 'host': host}
    with open(csv_file, 'a') as f:
        results.update({col: (np.mean(observations[col]) if isinstance(observations[col], list) else observations[col]) 
                        if col in observations else '' for col in state_cols})
        vals = [str(results[col]) for col in ['run_index', 'timestamp', 'host'] + state_cols]
        f.write(','.join(vals) + '\n')

def check_required_files():
    """Check if required files exist before running get_jmx_metrics"""
    required_files = [
        './status'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("Error: The following required files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, required=True, help="Host name (e.g., h1)")
    parser.add_argument("--index", type=int, required=True, help="Run index from schedule-1.csv")
    args = parser.parse_args()
    # Check for required files in a loop until they exist
    while not check_required_files():
        print("Waiting for required files to become available...")
        time.sleep(5)  # Wait 5 seconds before checking again
    
    # Once files exist, proceed with metrics collection
    print("Required files found, proceeding with JMX metrics collection...")
    get_jmx_metrics(args.host, BASE_JMX_PORT, args.index)