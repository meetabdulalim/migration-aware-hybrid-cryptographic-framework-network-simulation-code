import csv
import os
from config import CONFIG, RESULTS_RAW
from core.runs import latency_over_runs
from core.plotting import save_bar


DISPLAY_NAMES = {
    'classical': 'Classical',
    'pqc': 'PQC',
    'qkd': 'QKD',
    'hybrid': 'Proposed Hybrid',
    'naive_hybrid': 'Naive Hybrid',
}


def run_exp1():
    modes = CONFIG['paper_modes']
    labels, means, errs = [], [], []

    csv_path = os.path.join(RESULTS_RAW, 'exp1_mode_comparison.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['mode', 'mean_latency_ms', 'std', 'ci95', 'success_rate'])

        for mode in modes:
            st = latency_over_runs(
                hops=CONFIG['baseline_hops'],
                num_endpoints=CONFIG['baseline_endpoints'],
                arrival_rate=CONFIG['baseline_arrival_rate'],
                mode=mode,
            )
            labels.append(DISPLAY_NAMES.get(mode, mode))
            means.append(st['mean'])
            errs.append(st['ci95'])
            writer.writerow([mode, st['mean'], st['std'], st['ci95'], st['success_rate']])

    save_bar(
        labels,
        means,
        'Cryptographic Scheme',
        'Session Establishment Latency (ms)',
        'exp1_mode_comparison_latency.png',
        errs
    )