import csv
import os
from config import CONFIG, RESULTS_RAW
from core.runs import latency_over_runs
from core.plotting import save_multi_line


DISPLAY_NAMES = {
    'classical': 'Classical',
    'pqc': 'PQC',
    'qkd': 'QKD',
    'hybrid': 'Proposed Hybrid',
    'naive_hybrid': 'Naive Hybrid',
}


def run_exp3():
    csv_path = os.path.join(RESULTS_RAW, 'exp3_hop_impact.csv')
    series = []

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['mode', 'hops', 'mean_latency_ms', 'std', 'ci95'])

        for mode in CONFIG['paper_modes']:
            xs, ys, errs = [], [], []
            for h in CONFIG['hop_counts']:
                st = latency_over_runs(
                    hops=h,
                    num_endpoints=CONFIG['baseline_endpoints'],
                    arrival_rate=CONFIG['baseline_arrival_rate'],
                    mode=mode,
                )
                xs.append(h)
                ys.append(st['mean'])
                errs.append(st['ci95'])
                writer.writerow([mode, h, st['mean'], st['std'], st['ci95']])

            series.append((DISPLAY_NAMES.get(mode, mode), xs, ys, errs))
    # -------------------------
    # Plot
    # -------------------------
    save_multi_line(
        series,
        'Hop Count',
        'Session Establishment Latency (ms)',
        'exp3_hop_impact_all_schemes.png',
    )