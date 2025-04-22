import pandas as pd
import numpy as np
from pyDOE import lhs
import argparse
import os

def sample_configs(budget):
    """
    Generate samples using Latin Hypercube Sampling
    :param budget: the number of samples
    :return:
    """
    meta_info = pd.read_csv('meta/knob_meta.csv')
    knobs = pd.DataFrame(lhs(meta_info.shape[0], samples=budget))
    knobs = knobs.apply(
        lambda raw_knobs: (np.ceil(raw_knobs * meta_info['max'])).astype(int), axis=1)
    knobs.columns = meta_info['knob']
    knobs.reset_index(inplace=True)
    msg_cps = ['None', 'gzip', 'snappy', 'lz4']
    knobs['producer->compression_type'] = knobs['producer->compression_type'].apply(lambda x: msg_cps[x-1])
    knobs.to_csv(path_or_buf="schedule.csv", index=None)
    return knobs

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Benchmark")
    parser.add_argument("--budget", type=int, default=1000, help='LHS budget')
    args = parser.parse_args()
    if not os.path.exists("schedule.csv"):
        sample_configs(args.budget)
    else:
        print("schedule.csv already exists. Skipping sampling.")

