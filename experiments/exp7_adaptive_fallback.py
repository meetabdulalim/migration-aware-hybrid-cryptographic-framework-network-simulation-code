import csv
import os
import numpy as np
import matplotlib.pyplot as plt

from config import RESULTS_RAW, RESULTS_PLOTS, CONFIG
from models.protocol_model import simulate_session
from models.qkd_model import QKDResourcePool



def run_exp7():

    n_batches = 26
    sessions_per_batch = CONFIG['sessions_per_setting']
    runs = CONFIG['num_runs']

    outage_start = 10
    outage_end = 16   # inclusive

    x = np.arange(n_batches)

    # arrays [run, batch]
    succ = {'p': np.zeros((runs, n_batches)), 'n': np.zeros((runs, n_batches))}
    cov = {'p': np.zeros((runs, n_batches)), 'n': np.zeros((runs, n_batches))}

    for run in range(runs):
        for b in range(n_batches):
            qkd_available = not (outage_start <= b <= outage_end)
            proposed_pool = QKDResourcePool()
            no_fallback_pool = QKDResourcePool()
            ps = ns = 0
            pc = nc = 0.0
            for _ in range(sessions_per_batch):
                proposed_result = simulate_session(
                    hops=CONFIG['baseline_hops'],
                    num_endpoints=CONFIG['baseline_endpoints'],
                    arrival_rate=CONFIG['baseline_arrival_rate'],
                    mode='hybrid',
                    qkd_pool=proposed_pool,
                    force_qkd_success=True if qkd_available else False,
                    force_qkd_failure=False if qkd_available else True,
                )
                no_fallback_result = simulate_session(
                    hops=CONFIG['baseline_hops'],
                    num_endpoints=CONFIG['baseline_endpoints'],
                    arrival_rate=CONFIG['baseline_arrival_rate'],
                    mode='hybrid_no_fallback',
                    fallback=False,
                    qkd_pool=no_fallback_pool,
                    force_qkd_success=True if qkd_available else False,
                    force_qkd_failure=False if qkd_available else True,
                )
                ps += 1 if proposed_result['success'] else 0
                ns += 1 if no_fallback_result['success'] else 0
                pc += proposed_result['key_source_coverage']
                nc += no_fallback_result['key_source_coverage']
            succ['p'][run, b] = 100.0 * ps / sessions_per_batch
            succ['n'][run, b] = 100.0 * ns / sessions_per_batch
            cov['p'][run, b] = pc / sessions_per_batch
            cov['n'][run, b] = nc / sessions_per_batch

    def ci(a):
        return 1.96 * a.std(axis=0) / np.sqrt(runs)

    proposed_hybrid_success_rates = succ['p'].mean(axis=0)
    no_fallback_hybrid_success_rates = succ['n'].mean(axis=0)
    proposed_hybrid_resilience_scores = cov['p'].mean(axis=0)
    no_fallback_hybrid_resilience_scores = cov['n'].mean(axis=0)

    csv_path = os.path.join(RESULTS_RAW, 'exp7_adaptive_fallback_timeline.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'batch', 'qkd_usable',
            'proposed_hybrid_success_rate', 'proposed_success_ci95',
            'no_fallback_hybrid_success_rate', 'no_fallback_success_ci95',
            'proposed_hybrid_key_source_coverage', 'proposed_coverage_ci95',
            'no_fallback_hybrid_key_source_coverage', 'no_fallback_coverage_ci95',
        ])
        for b in range(n_batches):
            writer.writerow([
                b, 0 if outage_start <= b <= outage_end else 1,
                proposed_hybrid_success_rates[b], ci(succ['p'])[b],
                no_fallback_hybrid_success_rates[b], ci(succ['n'])[b],
                proposed_hybrid_resilience_scores[b], ci(cov['p'])[b],
                no_fallback_hybrid_resilience_scores[b], ci(cov['n'])[b],
            ])

    # -----------------------------
    # Plot raw simulation outputs directly
    # -----------------------------
    proposed_hybrid_success_plot = np.array(proposed_hybrid_success_rates)
    no_fallback_hybrid_success_plot = np.array(no_fallback_hybrid_success_rates)

    proposed_hybrid_resilience_plot = np.array(proposed_hybrid_resilience_scores)
    no_fallback_hybrid_resilience_plot = np.array(no_fallback_hybrid_resilience_scores)

    # -----------------------------
    # Plot
    # -----------------------------
    fig, ax1 = plt.subplots(figsize=(13, 7))
    ax2 = ax1.twinx()

    # Outage shaded window
    ax1.axvspan(outage_start - 0.5, outage_end + 0.5, alpha=0.15, color='gray')

    # Left axis: session success %
    ax1.plot(
        x, proposed_hybrid_success_plot,
        marker='o', linewidth=2.8, markersize=8,
        color='tab:blue',
        label='Proposed Hybrid: Session Success Rate'
    )
    ax1.plot(
        x, no_fallback_hybrid_success_plot,
        marker='s', linewidth=2.8, markersize=8,
        color='tab:green',
        label='No-Fallback Hybrid: Session Success Rate'
    )

    # Right axis: resilience
    ax2.plot(
        x, proposed_hybrid_resilience_plot,
        marker='^', linestyle='--', linewidth=2.8, markersize=8,
        color='red',
        label='Proposed Hybrid: Key-Source Coverage'
    )
    ax2.plot(
        x, no_fallback_hybrid_resilience_plot,
        marker='d', linestyle='--', linewidth=2.8, markersize=8,
        color='tab:orange',
        label='No-Fallback Hybrid: Key-Source Coverage'
    )

    ax1.set_xlabel('Session Batch Index')
    ax1.set_ylabel('Session Success Rate (%)')
    ax2.set_ylabel('Key-Source Coverage')
    ax1.set_ylim(0, 105)
    ax2.set_ylim(0, 1.05)
    ax1.grid(True, alpha=0.3)

    # Outage label
    ax1.text(
        (outage_start + outage_end) / 2,
        8,
        'QKD outage window',
        ha='center',
        va='bottom',
        fontsize=12
    )

    # Annotation 1: continuity preserved
    ax1.annotate(
        'Continuity preserved',
        xy=(13, proposed_hybrid_success_plot[13]),
        xytext=(18.0, 90),
        fontsize=12,
        arrowprops=dict(arrowstyle='->', lw=1.6)
    )

    # Annotation 2: resilience maintained
    ax2.annotate(
        '   Fallback keeps classical+PQC\n(2 of 3 key sources)',
        xy=(13, proposed_hybrid_resilience_plot[13]),
        xytext=(18.0, 0.70),
        fontsize=12,
        arrowprops=dict(arrowstyle='->', lw=1.6)
    )

    # Annotation 3: no-fallback degradation
    ax1.annotate(
        '   No-Fallback Hybrid\ndegrades under outage',
        xy=(13, no_fallback_hybrid_success_plot[13]),
        xytext=(2.0, 32),
        fontsize=12,
        arrowprops=dict(arrowstyle='->', lw=1.6)
    )

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='lower left', fontsize=11)

    plt.tight_layout()
    plt.savefig(
        os.path.join(RESULTS_PLOTS, 'exp7_adaptive_fallback_timeline.png'),
        dpi=300
    )
    plt.close()