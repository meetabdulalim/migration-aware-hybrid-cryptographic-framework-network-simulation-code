import csv
import os
import numpy as np

from config import CONFIG, RESULTS_RAW
from models.protocol_model import simulate_session
from models.qkd_model import QKDResourcePool


def _collect(mode):
    runs, sess = CONFIG['num_runs'], CONFIG['sessions_per_setting']
    all_lat, qkd_lat, ok, qkd, total = [], [], 0, 0, 0
    for _ in range(runs):
        pool = QKDResourcePool()
        for _ in range(sess):
            r = simulate_session(mode=mode, qkd_pool=pool)
            total += 1
            if r['success']:
                ok += 1
                all_lat.append(r['latency_ms'])
            if r['qkd_used']:
                qkd += 1
                qkd_lat.append(r['latency_ms'])
    return ok / total, qkd / total, float(np.mean(all_lat)), float(np.mean(qkd_lat))


def run_exp9():
    saved = CONFIG['naive_extra_rounds']
    path = os.path.join(RESULTS_RAW, 'exp9_naive_sensitivity.csv')
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['scheme', 'naive_extra_rounds', 'success_rate', 'qkd_secured_share',
                    'mean_latency_all_ms', 'mean_latency_qkd_sessions_ms'])
        p = _collect('hybrid')
        w.writerow(['proposed', '-'] + [round(v, 4) for v in p])
        for k in CONFIG['naive_extra_rounds_sweep']:
            CONFIG['naive_extra_rounds'] = k
            n = _collect('naive_hybrid')
            w.writerow(['naive', k] + [round(v, 4) for v in n])
    CONFIG['naive_extra_rounds'] = saved
