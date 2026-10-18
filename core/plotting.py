import matplotlib.pyplot as plt
import os
from config import RESULTS_PLOTS


def save_bar(labels, values, xlabel, ylabel, filename, errors=None):
    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, yerr=errors, capsize=5)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=15)
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PLOTS, filename), dpi=300)
    plt.close()


def save_line(x, y, xlabel, ylabel, filename, yerr=None, label=None):
    plt.figure(figsize=(8, 5))
    plt.errorbar(x, y, yerr=yerr, marker='o', capsize=4, label=label)
    if label:
        plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PLOTS, filename), dpi=300)
    plt.close()


def save_multi_line(series, xlabel, ylabel, filename):
    plt.figure(figsize=(8, 5))
    markers = ['o', 's', '^', 'D', 'x', '*', 'v']

    for idx, item in enumerate(series):
        if len(item) == 4:
            label, x, y, err = item
            plt.errorbar(x, y, yerr=err, marker=markers[idx % len(markers)], capsize=4, label=label)
        else:
            label, x, y = item
            plt.plot(x, y, marker=markers[idx % len(markers)], label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PLOTS, filename), dpi=300)
    plt.close()


def save_grouped_bar(categories, series_dict, xlabel, ylabel, filename):
    import numpy as np

    plt.figure(figsize=(10, 5))
    x = np.arange(len(categories))
    num_series = len(series_dict)
    width = 0.35 if num_series == 2 else 0.8 / max(num_series, 1)

    for idx, (label, values) in enumerate(series_dict.items()):
        offset = (idx - (num_series - 1) / 2) * width
        plt.bar(x + offset, values, width=width, label=label)

    plt.xticks(x, categories, rotation=10)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.ylim(0, 1.05)
    plt.legend()
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_PLOTS, filename), dpi=300)
    plt.close()