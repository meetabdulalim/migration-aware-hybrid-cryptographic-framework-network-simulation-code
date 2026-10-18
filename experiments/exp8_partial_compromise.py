import csv
import os
import numpy as np
import matplotlib.pyplot as plt

from config import CONFIG, RESULTS_RAW, RESULTS_PLOTS
from models.protocol_model import simulate_session, _mode_flags
from models.qkd_model import QKDResourcePool

SCHEMES = [
    ('Classical',       'classical'),
    ('PQC',             'pqc'),
    ('QKD',             'qkd'),
    ('Naive Hybrid',    'naive_hybrid'),
    ('Proposed Hybrid', 'hybrid'),
]

SCENARIOS = [
    # (label, compromised set B)
    ('None compromised',  set()),
    ('Classical broken',  {'C'}),
    ('PQC broken',        {'P'}),
    ('QKD broken',        {'Q'}),
    ('Classical+PQC',     {'C', 'P'}),
    ('Classical+QKD',     {'C', 'Q'}),
    ('PQC+QKD',           {'P', 'Q'}),
    ('All broken',        {'C', 'P', 'Q'}),
]


def _sessions(mode):
    """(established, contributing-source set) for num_runs x sessions_per_setting sessions."""
    flags = _mode_flags(mode)
    out = []
    for _ in range(CONFIG['num_runs']):
        pool = QKDResourcePool()
        for _ in range(CONFIG['sessions_per_setting']):
            r = simulate_session(mode=mode, qkd_pool=pool)
            src = set()
            if flags['use_classical']:
                src.add('C')
            if flags['use_pqc']:
                src.add('P')
            if r['qkd_used']:
                src.add('Q')
            out.append((r['success'], frozenset(src)))
    return out


def run_exp8():
    results = {label: [] for label, _ in SCHEMES}
    csv_path = os.path.join(RESULTS_RAW, 'exp8_partial_compromise.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['scenario', 'scheme', 'established_fraction', 'secure_fraction',
                    'secure_ci95', 'exposed_given_established'])
        sessions = {label: _sessions(mode) for label, mode in SCHEMES}
        for scen, broken in SCENARIOS:
            for label, _ in SCHEMES:
                s = sessions[label]
                n = len(s)
                est = sum(1 for ok, _ in s if ok)
                sec = sum(1 for ok, src in s if ok and (src - broken))
                p = sec / n
                ci = 1.96 * np.sqrt(p * (1 - p) / n)
                exposed = (est - sec) / est if est else float('nan')
                results[label].append(p)
                w.writerow([scen, label, round(est / n, 4), round(p, 4),
                            round(ci, 4), round(exposed, 4)])

    x = np.arange(len(SCENARIOS))
    width = 0.16
    colors = {'Classical': '#1f77b4', 'PQC': '#9d4390', 'QKD': '#ff7f0e',
              'Naive Hybrid': '#d62728', 'Proposed Hybrid': '#2ca02c'}
    fig, ax = plt.subplots(figsize=(15, 7))
    for i, (label, _) in enumerate(SCHEMES):
        ax.bar(x + (i - 2) * width, results[label], width=width, label=label,
               color=colors[label], alpha=0.88)
    ax.set_xticks(x)
    ax.set_xticklabels([s[0] for s in SCENARIOS], rotation=15, ha='right', fontsize=10)
    ax.set_ylabel('Fraction of sessions with a secret key', fontsize=12)
    ax.set_xlabel('Compromised key sources (adversary knows their contribution)', fontsize=12)
    ax.set_ylim(0, 1.08)
    ax.grid(True, axis='y', alpha=0.25)
    ax.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PLOTS, 'exp8_partial_compromise.png'), dpi=300)
    plt.close()
