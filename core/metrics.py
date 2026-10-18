import numpy as np


def summarize(values):
    arr = np.array(values, dtype=float)
    mean = float(np.mean(arr)) if len(arr) else 0.0
    std = float(np.std(arr)) if len(arr) else 0.0
    ci95 = 1.96 * std / np.sqrt(len(arr)) if len(arr) > 0 else 0.0
    return {'mean': mean, 'std': std, 'ci95': ci95}


def ratio(successes, total):
    return float(successes) / float(total) if total else 0.0
