import csv
import os
import numpy as np
import matplotlib.pyplot as plt

from config import CONFIG, RESULTS_RAW, RESULTS_PLOTS
from models.protocol_model import simulate_session
from models.qkd_model import QKDResourcePool

SCHEMES = [('hybrid', 'Proposed Hybrid', 'o-', 'C0'),
           ('naive_hybrid', 'Naive Hybrid', '^--', 'C3'),
           ('qkd', 'QKD-only', 's:', 'C2')]


def _point(mode, availability, coverage):
    runs, sess = CONFIG['num_runs'], CONFIG['sessions_per_setting']
    ok = total = 0
    lat, cov = [], 0.0
    for _ in range(runs):
        pool = QKDResourcePool(availability=availability)
        for _ in range(sess):
            r = simulate_session(hops=CONFIG['baseline_hops'], mode=mode,
                                 qkd_prob=availability, qkd_pool=pool)
            total += 1
            cov += r['key_source_coverage']
            if r['success']:
                ok += 1
                lat.append(r['latency_ms'])
    return {'success_rate': ok / total,
            'key_source_coverage': cov / total,
            'mean_latency_ms': float(np.mean(lat)) if lat else float('nan')}


def run_exp10():
    avs, covs = CONFIG['qkd_availability_sweep'], CONFIG['qkd_coverage_sweep']
    saved = CONFIG['qkd_link_coverage']
    rows = []
    for c in covs:
        CONFIG['qkd_link_coverage'] = c
        for mode, _, _, _ in SCHEMES:
            for a in avs:
                rows.append(dict(coverage=c, mode=mode, availability=a, **_point(mode, a, c)))
    CONFIG['qkd_link_coverage'] = saved

    fields = ['coverage', 'mode', 'availability', 'success_rate', 'key_source_coverage', 'mean_latency_ms']
    with open(os.path.join(RESULTS_RAW, 'exp10_availability_sweep.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})

    def get(mode, c, key):
        return [r[key] for r in rows if r['mode'] == mode and r['coverage'] == c]

    c0 = saved
    fig, ax = plt.subplots(1, 3, figsize=(17, 5.2))
    for mode, label, st, col in SCHEMES:
        ax[0].plot(avs, get(mode, c0, 'success_rate'), st, color=col, lw=2.2, ms=8, label=label)
        ax[1].plot(avs, get(mode, c0, 'key_source_coverage'), st, color=col, lw=2.2, ms=8, label=label)
    for c, ls in zip(covs, ['-', '--', ':']):
        ax[2].plot(avs, get('naive_hybrid', c, 'success_rate'), ls, marker='^', color='C3', lw=2,
                   label='Naive, link coverage %.2f' % c)
    ax[2].plot(avs, get('hybrid', c0, 'success_rate'), 'o-', color='C0', lw=2.2, label='Proposed (all coverages)')
    ax[0].set_title('(a) Session success (link coverage %.2f)' % c0)
    ax[1].set_title('(b) Key-source coverage (link coverage %.2f)' % c0)
    ax[2].set_title('(c) Effect of link coverage on session success')
    ax[0].set_ylabel('Fraction of sessions with a key')
    ax[1].set_ylabel('Key-source coverage')
    ax[2].set_ylabel('Fraction of sessions with a key')
    for a in ax:
        a.set_xlabel('QKD availability probability')
        a.set_ylim(0, 1.05)
        a.grid(True, alpha=0.3)
        a.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PLOTS, 'exp10_availability_sweep.png'), dpi=300)
    plt.close()
