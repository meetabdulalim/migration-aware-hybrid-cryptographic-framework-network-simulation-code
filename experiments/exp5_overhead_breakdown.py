import csv
import os
from config import RESULTS_RAW, CONFIG
from core.metrics import summarize
from core.plotting import save_bar
from models.protocol_model import simulate_session
from models.qkd_model import QKDResourcePool


def run_exp5():
    comps = {
        'Classical Key Exchange': [],
        'PQC Key Exchange': [],
        'QKD Retrieval': [],
        'Key Combiner / KDF': [],
    }

    runs, sess = CONFIG['num_runs'], CONFIG['sessions_per_setting']
    run_means = {k: [] for k in comps}
    for _ in range(runs):
        pool = QKDResourcePool()
        acc = {k: [] for k in comps}
        for _ in range(sess):
            r = simulate_session(mode='hybrid', qkd_pool=pool)
            if not r['success']:
                continue
            acc['Classical Key Exchange'].append(r['classical_ms'])
            acc['PQC Key Exchange'].append(r['pqc_ms'])
            acc['QKD Retrieval'].append(r['qkd_ms'] + r['qkd_wait_ms'])
            acc['Key Combiner / KDF'].append(r['kdf_ms'])
        for k in comps:
            run_means[k].append(sum(acc[k]) / len(acc[k]))
    comps = run_means

    labels = list(comps.keys())
    values = [sum(v) / len(v) for v in comps.values()]
    errs = [summarize(v)['ci95'] for v in comps.values()]

    csv_path = os.path.join(RESULTS_RAW, 'exp5_overhead_breakdown.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['component', 'mean_ms', 'ci95'])
        for l, v, e in zip(labels, values, errs):
            writer.writerow([l, v, e])

    save_bar(
        labels,
        values,
        'Protocol Component',
        'Mean Session Setup Delay (ms)',
        'exp5_overhead_breakdown.png',
        errs
    )