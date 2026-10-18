import numpy as np

from config import CONFIG
from core.metrics import summarize
from models.protocol_model import simulate_session
from models.qkd_model import QKDResourcePool


def latency_over_runs(qkd_prob=None, **session_kwargs):
    """B/item 14: num_runs independent runs (fresh QKD pool each) x sessions_per_setting sessions.
    The unit of replication is the run: mean/std/ci95 are taken over per-run mean latencies of
    established sessions (95% CI = 1.96*std/sqrt(num_runs)); success_rate pools all sessions."""
    runs, sess = CONFIG['num_runs'], CONFIG['sessions_per_setting']
    run_means, ok, total = [], 0, 0
    for _ in range(runs):
        pool = QKDResourcePool(availability=qkd_prob)
        vals = []
        for _ in range(sess):
            r = simulate_session(qkd_pool=pool, qkd_prob=qkd_prob, **session_kwargs)
            total += 1
            if r['success']:
                ok += 1
                vals.append(r['latency_ms'])
        if vals:
            run_means.append(float(np.mean(vals)))
    s = summarize(run_means)
    s['success_rate'] = ok / total
    return s
