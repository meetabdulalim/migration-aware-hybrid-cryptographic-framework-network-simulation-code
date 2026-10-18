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


def run_exp2():
    csv_path = os.path.join(RESULTS_RAW, 'exp2_scalability.csv')
    series = []

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['mode', 'endpoints', 'mean_latency_ms', 'std', 'ci95'])

        for mode in CONFIG['paper_modes']:
            xs, ys, errs = [], [], []
            for n in CONFIG['endpoints_list']:
                arrival = min(CONFIG['baseline_arrival_rate'] + n / 40.0, CONFIG['service_rate'] - 1.0)
                st = latency_over_runs(
                    hops=CONFIG['baseline_hops'],
                    num_endpoints=n,
                    arrival_rate=arrival,
                    mode=mode,
                )
                xs.append(n)
                ys.append(st['mean'])
                errs.append(st['ci95'])
                writer.writerow([mode, n, st['mean'], st['std'], st['ci95']])

            series.append((DISPLAY_NAMES.get(mode, mode), xs, ys, errs))

    save_multi_line(
        series,
        'Network Size (Number of Endpoints)',
        'Session Establishment Latency (ms)',
        'exp2_scalability_all_schemes.png',
    )