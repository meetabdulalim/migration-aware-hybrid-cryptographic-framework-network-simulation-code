import csv
import os
from config import RESULTS_RAW, CONFIG
from core.metrics import summarize
from core.plotting import save_grouped_bar
from models.protocol_model import simulate_session
from models.qkd_model import QKDResourcePool


SCENARIOS = [
    ('Baseline Hybrid\n(Classical+PQC)', {'mode': 'hybrid_no_qkd', 'num_endpoints': 60, 'arrival_rate': 8, 'qkd_prob': 0.0}),
    ('Partial / Intermittent\nQKD Availability', {'mode': 'hybrid', 'num_endpoints': 80, 'arrival_rate': 10, 'qkd_prob': 0.40}),
    ('QKD-Enhanced Hybrid\n(Classical+PQC+QKD)', {'mode': 'hybrid', 'num_endpoints': 80, 'arrival_rate': 10, 'qkd_prob': 0.85}),
]


def run_exp6():
    labels = []
    success_means = []
    resilience_means = []

    csv_path = os.path.join(RESULTS_RAW, 'exp6_migration_aware.csv')

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['scenario', 'session_success_rate', 'success_ci95', 'key_source_coverage', 'coverage_ci95'])

        for label, params in SCENARIOS:
            runs, sess = CONFIG['num_runs'], CONFIG['sessions_per_setting']
            run_success, run_cov = [], []
            for _ in range(runs):
                pool = QKDResourcePool(availability=params['qkd_prob'])
                ok, cov = 0, 0.0
                for _ in range(sess):
                    r = simulate_session(
                        hops=CONFIG['baseline_hops'],
                        mode=params['mode'],
                        num_endpoints=params['num_endpoints'],
                        arrival_rate=params['arrival_rate'],
                        qkd_prob=params['qkd_prob'],
                        qkd_pool=pool,
                    )
                    ok += 1 if r['success'] else 0
                    cov += r['key_source_coverage']
                run_success.append(ok / sess)
                run_cov.append(cov / sess)

            s_success = summarize(run_success)
            s_res = summarize(run_cov)

            labels.append(label)
            success_means.append(s_success['mean'])
            resilience_means.append(s_res['mean'])

            writer.writerow([label, s_success['mean'], s_success['ci95'], s_res['mean'], s_res['ci95']])

    save_grouped_bar(
        labels,
        {
            'Key-Source Coverage': resilience_means,
            'Session Success Rate': success_means,
        },
        'Deployment Scenario',
        'Normalized Score',
        'exp6_migration_aware.png',
    )