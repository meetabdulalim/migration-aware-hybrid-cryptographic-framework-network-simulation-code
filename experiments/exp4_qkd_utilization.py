import csv
import os
import numpy as np
import matplotlib.pyplot as plt

from config import CONFIG, RESULTS_RAW, RESULTS_PLOTS
from models.protocol_model import simulate_session
from models.qkd_model import QKDResourcePool


def _batch(mode, n_endpoints, rate_kbps):
    """Run num_runs independent batches (fresh QKD pool each) of
    sessions_per_setting sessions; return aggregate statistics."""
    runs, sess = CONFIG['num_runs'], CONFIG['sessions_per_setting']
    total = ok = qkd_ok = 0
    consumed = 0
    lat, wait = [], []
    util = []
    for _ in range(runs):
        pool = QKDResourcePool(generation_rate_kbps=rate_kbps)
        for _ in range(sess):
            r = simulate_session(num_endpoints=n_endpoints, mode=mode, qkd_pool=pool)
            total += 1
            if r['success']:
                ok += 1
                lat.append(r['latency_ms'])
                wait.append(r['qkd_wait_ms'])
            if r['qkd_used']:
                qkd_ok += 1
            consumed += r['qkd_consumed_bits']
        den = pool.total_generated_bits + CONFIG['qkd_pool_capacity_bits'] * CONFIG['qkd_initial_fill_ratio']
        util.append(pool.total_consumed_bits / den)
    return {
        'success_rate': ok / total,
        'qkd_secured_share': qkd_ok / total,
        'consumed_bits_per_session': consumed / total,
        'mean_latency_ms': float(np.mean(lat)) if lat else float('nan'),
        'mean_wait_ms': float(np.mean(wait)) if wait else float('nan'),
        'pool_utilization': float(np.mean(util)),
    }


def run_exp4():
    modes = [('hybrid', 'Proposed Hybrid'), ('naive_hybrid', 'Naive Hybrid')]
    sizes = CONFIG['endpoints_list']
    rates = CONFIG['qkd_scarcity_rates_kbps']
    base_rate = CONFIG['qkd_generation_rate_kbps']

    fields = ['panel', 'x', 'mode', 'success_rate', 'qkd_secured_share',
              'consumed_bits_per_session', 'mean_latency_ms', 'mean_wait_ms', 'pool_utilization']
    rows = []
    for mode, _ in modes:
        for n in sizes:
            rows.append(dict(panel='size', x=n, mode=mode, **_batch(mode, n, base_rate)))
        for rate in rates:
            rows.append(dict(panel='rate', x=rate, mode=mode,
                             **_batch(mode, CONFIG['baseline_endpoints'], rate)))

    with open(os.path.join(RESULTS_RAW, 'exp4_qkd_utilization.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})

    def series(panel, mode, key):
        return [r[key] for r in rows if r['panel'] == panel and r['mode'] == mode]

    fig, ax = plt.subplots(1, 3, figsize=(17, 5.2))
    styles = {'hybrid': ('o-', 'C0'), 'naive_hybrid': ('^--', 'C3')}
    for mode, label in modes:
        st, c = styles[mode]
        ax[0].plot(sizes, series('size', mode, 'consumed_bits_per_session'), st, color=c, lw=2.2, ms=8, label=label)
        ax[1].plot(rates, series('rate', mode, 'success_rate'), st, color=c, lw=2.2, ms=8, label=label + ' (key established)')
        if mode == 'hybrid':
            ax[1].plot(rates, series('rate', mode, 'qkd_secured_share'), 's:', color='C2', lw=2.2, ms=7,
                       label='Proposed Hybrid (QKD-secured)')
        ax[2].plot(rates, series('rate', mode, 'mean_latency_ms'), st, color=c, lw=2.2, ms=8, label=label)
    ax[0].set_xlabel('Network size (endpoints)')
    ax[0].set_ylabel('QKD bits consumed per session')
    ax[0].set_title('(a) Consumption vs. network size')
    ax[1].set_xscale('log')
    ax[1].set_xlabel('QKD generation rate (kbps, log)')
    ax[1].set_ylabel('Fraction of sessions')
    ax[1].set_ylim(0, 1.05)
    ax[1].set_title('(b) QKD scarcity: session outcome')
    ax[2].set_xscale('log')
    ax[2].set_xlabel('QKD generation rate (kbps, log)')
    ax[2].set_ylabel('Mean latency of established sessions (ms)')
    ax[2].set_title('(c) QKD scarcity: latency')
    for a in ax:
        a.grid(True, alpha=0.3)
        a.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PLOTS, 'exp4_qkd_utilization.png'), dpi=300)
    plt.close()
