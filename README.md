# A Migration-Aware Hybrid Cryptographic Framework With Adaptive Fallback— Simulation Code


> **Simulation source code for the paper:**
>
> *"A Migration-Aware Hybrid Cryptographic Framework With Adaptive Fallback for Classical, Post-Quantum, and Quantum Key Distribution Security"*


---

## Overview

This repository contains the complete Python-based, **session-level Monte-Carlo, network-aware simulation** used to produce all performance evaluation results (Section 6, Figures 4–12 and Tables 3–6) of the paper.

The simulator models **secure end-to-end session establishment** across a multi-hop heterogeneous network where classical cryptography (e.g., ECDHE), post-quantum cryptography (e.g., ML-KEM-768, formerly Kyber-768), and quantum key distribution (QKD) coexist. It operates at the **architecture level** — capturing realistic timing behavior, QKD resource constraints, and failure modes derived from published hardware benchmarks — rather than re-implementing actual cryptographic primitives.

The central research question addressed by the simulation:

> *Can a migration-aware hybrid framework deliver 100% session continuity, bounded latency, and robust resilience via endpoint-local key composition and adaptive fallback, within multi-hop networks of partially trusted nodes and partially or temporarily unavailable QKD infrastructure?*

The answer is validated through **ten controlled experiments** across five cryptographic baseline schemes, with **120 independent runs × 300 sessions** per configuration.

---

## Table of Contents

- [Key Contributions](#key-contributions)
- [Framework Architecture](#framework-architecture)
- [Research Questions & Experiments](#research-questions--experiments)
- [Project Structure](#project-structure)
- [Simulation Models](#simulation-models)
- [Cryptographic Modes](#cryptographic-modes)
- [Key Simulation Parameters](#key-simulation-parameters)
- [Installation](#installation)
- [Contributing](#contributing)
- [Usage](#usage)
  - [Run All Experiments](#run-all-experiments)
  - [Run Individual Experiments](#run-individual-experiments)
- [Results](#results)
  - [Experiment 1: Baseline Latency Comparison](#experiment-1-baseline-latency-comparison)
  - [Experiment 5: Overhead Breakdown](#experiment-5-overhead-breakdown)
  - [Experiment 6: Migration-Aware Performance](#experiment-6-migration-aware-performance)
  - [Experiment 8: Secret-Key Sessions Under Partial Compromise](#experiment-8-secret-key-sessions-under-partial-compromise)
- [Output Files](#output-files)
- [Reproducibility](#reproducibility)
- [Design Decisions & Validity](#design-decisions--validity)
- [Citation](#citation)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Key Contributions

This simulation code directly validates the following technical contributions of the paper:

1. **Migration-aware hybrid framework** — integrates Classical (ECDHE), PQC (ML-KEM-768), and QKD within a single unified session establishment architecture.
2. **Endpoint-local robust hybrid key composition** — implements Algorithm 1 from the paper:
   ```
   KS_i = KDF(KC_i ∥ KP_i ∥ [KQ_i] ∥ ctx_i)
   ```
   The session key remains secure as long as **at least one** source is uncompromised.
3. **Adaptive fallback mechanism** — when QKD entropy is unavailable, the system automatically continues with Classical + PQC only, maintaining 100% session success.
4. **Three-mode migration model** — Mode 0 (Classical+PQC), Mode 1 (Intermittent QKD), Mode 2 (Full QKD) — supporting phased deployment without infrastructure replacement.
5. **Secret-key sessions under compromise** — the key stays secret whenever one contributing source is uncompromised (Lemma 1); fraction of secret-key sessions measured per compromise scenario.

---

## Framework Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Endpoint A / B                           │
│  ┌──────────────────── Hybrid Key Management Layer ──────────┐  │
│  │  Classical KA     PQC KEM          QKD Interface          │  │
│  │  (ECDHE)→KC_i    (ML-KEM-768)→KP_i (BB84/E91)→KQ_i        │  │
│  │                                    [QKD Avail. Monitor]   │  │
│  │                        ↓                                  │  │
│  │  Key_Buffer = KC_i ∥ KP_i ∥ [ KQ_i if available ]         │  │
│  │                        ↓                                  │  │
│  │       KS_i = KDF(Key_Buffer ∥ ctx_i)   ← Endpoint-local   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                    Secure erasure of KC_i, KP_i, KQ_i           │
│  ┌──────────────────── Secure Channel Layer ──────────────────┐ │
│  │           AEAD-Encrypted Application Data                  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

```

**Three operational modes:**

| Mode | Cryptographic Sources | When Used |
|------|-----------------------|-----------|
| **Mode 0** | Classical + PQC only | Initial deployment / QKD absent |
| **Mode 1** | Classical + PQC + QKD (intermittent) | Partial QKD infrastructure |
| **Mode 2** | Classical + PQC + QKD (full) | Complete QKD deployment |

Modes 1 and 2 share the same key-composition logic (Algorithm 1 tests only `mode > 0`); they differ in how much of the network has QKD coverage. Exp 6 does not simulate Mode 2 as full coverage: its "QKD-Enhanced Hybrid" scenario uses availability 0.85 and per-link coverage 0.82.

---

## Research Questions & Experiments

| # | Research Question | Experiment | Key Result |
|---|-------------------|------------|------------|
| RQ1 | What is the latency overhead vs. baselines? | Exp 1 | Proposed hybrid: **29.73 ms, 100% success**; naïve hybrid (no fallback): **39.85 ms, 46.5% success** (successful sessions only). |
|  | What drives the hybrid overhead? | Exp 5 | KDF = **0.30 ms**; PQC key exchange = 8.00 ms (largest component). |
| RQ2 | How does the framework scale with network size? | Exp 2 | Approximately linear growth: **+4.55 ms** from 20→100 endpoints (part of it from the arrival rate 6 + n/40). |
|  | How does multi-hop path length affect latency? | Exp 3 | Small hop dependence: **+1.39 ms** from 1→5 hops (longer paths make a QKD path less likely, so fewer sessions pay QKD coordination). |
| RQ3 | How efficiently is QKD entropy utilized? | Exp 4 | Same QKD use per session as the naïve hybrid (within 2%); the naïve hybrid fails without QKD (~57% of sessions at baseline), the proposed hybrid keeps 100% success, even at 1 kbps generation rate. Naïve extra-rounds sensitivity: Exp 9 (Table 5). |
| RQ4 | Does the framework support incremental migration? | Exp 6 | **100% session success** at 0%, 40%, and 85% QKD availability; key-source coverage 0.667 / 0.739 / 0.821. |
| RQ5 | Does adaptive fallback preserve continuity under QKD outage? | Exp 7, Exp 10 | **100% continuity** during an *injected* outage (QKD is forced up/down by construction); no-fallback configuration = **0% success**. Exp 10 measures the dependence on QKD availability (0–1) and link coverage (0.6, 0.82, 0.95). |
| RQ6 | Is the hybrid composition robust under partial compromise? | Exp 8 | Secret key in 100% of sessions under every single- and dual-source compromise except Classical+PQC (44%: only QKD-assisted sessions stay secret). |

---

## Project Structure

```
.
├── main.py                        # Entry point — runs all 10 experiments sequentially
├── config.py                      # All simulation parameters
├── requirements.txt               # Python dependencies
│
├── models/                        # Core simulation building blocks
│   ├── network_model.py           # Watts–Strogatz topology, shortest-path routing, QKD path availability  
│   ├── crypto_model.py            # Stochastic delays for classical, PQC, KDF operations
│   ├── qkd_model.py               # QKD resource pool: generation, replenishment, acquisition
│   ├── traffic_model.py           # Analytic M/M/1 mean waiting time (deterministic; no random arrivals)
│   └── protocol_model.py          # Master session simulator combining all sub-models
│
├── experiments/                   # One file per experiment (Exp 1–10)
│   ├── exp1_mode_comparison.py    # Fig. 4 — Baseline latency across 5 cryptographic schemes
│   ├── exp2_scalability.py        # Fig. 5 — Network size scaling (20–100 endpoints)
│   ├── exp3_hop_impact.py         # Fig. 6 — Hop count impact (1–5 hops)
│   ├── exp4_qkd_utilization.py    # Fig. 8 — QKD consumption vs. network size and QKD scarcity (simulated)
│   ├── exp5_overhead_breakdown.py # Fig. 7 — Per-component latency decomposition
│   ├── exp6_migration_aware.py    # Fig. 9 — Migration-phase performance
│   ├── exp7_adaptive_fallback.py  # Fig. 10 — injected QKD outage and adaptive fallback behavior
│   ├── exp8_partial_compromise.py # Fig. 11 — secret-key sessions under partial compromise
│   ├── exp9_naive_sensitivity.py  # Table 5 — naive-hybrid extra-rounds sensitivity
│   └── exp10_availability_sweep.py # Fig. 12 — QKD availability x link-coverage sweep
│
├── core/                          # Shared utilities
│   ├── metrics.py                 # Mean, standard deviation, 95% CI computation
│   ├── plotting.py                # Matplotlib-based figure generation helpers
│   └── utils.py                   # Seed management, reproducibility helpers
│
└── results/
    ├── raw/                       # CSV files — one per experiment (pre-computed)
    └── plots/                     # PNG figures matching paper Figs. 4–12 (pre-computed)
```

---

## Simulation Models

| Model | File | What It Does |
|-------|------|---------------|
| Network | `models/network_model.py` | Watts–Strogatz topology (`k=4`, `p=0.25`; generated once per network size and cached, so all runs share it), shortest-path routing, per-hop delay (0.8–1.6 ms), QKD path availability (`0.82^hops`) |
| Cryptographic delays | `models/crypto_model.py` | Per-operation latency sampled from `random.uniform()` (e.g., PQC key exchange: 6–10 ms, KDF: 0.1–0.5 ms) — see `config.py` for all ranges |
| QKD resource pool | `models/qkd_model.py` | Finite entropy pool (60,000-bit capacity, 96 kbps generation) with acquisition/replenishment logic; triggers fallback when depleted |
| Traffic | `models/traffic_model.py` | Analytic M/M/1 mean waiting time 250·λ/(μ(μ−λ)) ms (a calibrated scaling), capped at 60 ms; sessions are drawn independently and the QKD pool is replenished by 1000/λ ms between sessions |
| Protocol (master) | `models/protocol_model.py` | `simulate_session()` — combines all of the above into one session attempt; used by all experiments (Exp 1–10) |

---

## Cryptographic Modes

The simulator supports the following operational modes, corresponding to the baseline schemes and proposed framework described in the paper:

| Mode | Classical | PQC | QKD | Adaptive Fallback | Paper Role |
|------|:---------:|:---:|:---:|:-----------------:|------------|
| `classical` | ✓ | — | — | — | Legacy baseline |
| `pqc` | — | ✓ | — | — | PQC migration baseline |
| `qkd` | — | — | ✓ | ✗ (fails if QKD unavailable) | QKD-only baseline |
| `naive_hybrid` | ✓ | ✓ | ✓ | ✗ (extra overhead) | Naïve hybrid baseline |
| `hybrid_no_fallback` | ✓ | ✓ | ✓ | ✗ (fails if QKD unavailable) | No-fallback comparison (Exp 7) |
| `hybrid_no_qkd` | ✓ | ✓ | — | — | Mode 0 / migration baseline (Exp 6) |
| `hybrid` | ✓ | ✓ | ✓ (optional) | ✓ → Classical+PQC | **Proposed framework** |

**Key-source coverage** (share of the three sources — classical, PQC, QKD — that contributed to the session key; measured, no calibrated constants):

| Configuration | Coverage |
|---------------|:--------:|
| Classical only / PQC only | 0.33 |
| QKD only (QKD available / unavailable) | 0.33 / 0 (no key) |
| Naïve hybrid (QKD available / unavailable) | 1.00 / 0 (no key, no fallback) |
| **Proposed hybrid** (QKD used / fallback Classical+PQC) | **1.00 / 0.67** |

Coverage measures source diversity, not security strength. Secrecy under compromise follows from Lemma 1 and is evaluated in [Experiment 8](#experiment-8-secret-key-sessions-under-partial-compromise).

---

## Key Simulation Parameters

All parameters are defined in `config.py` as a single `CONFIG` dictionary. Key parameters:

```python
# Reproducibility & statistical reliability
'seed': 42,
'num_runs': 120,              # Independent runs per configuration
'sessions_per_setting': 300,  # Sessions per run

# Network topology (Watts–Strogatz)
'baseline_endpoints': 60,
'endpoints_list': [20, 40, 60, 80, 100],
'avg_degree': 4,
'rewire_prob': 0.25,
'per_hop_delay_ms': (0.8, 1.6),
'qkd_link_coverage': 0.82,    # Per-link QKD coverage (path availability = 0.82^hops)
'baseline_hops': 3,
'hop_counts': [1, 2, 3, 4, 5],

# Cryptographic delays (ms)
'classical_crypto_ms': (0.8, 1.5),
'pqc_delay_ms': (6.0, 10.0),
'kdf_delay_ms': (0.1, 0.5),
'classical_rounds': 2,         # Authenticated control-plane round-trips
'qkd_control_rounds': 3,       # QKD coordination round-trips
'naive_extra_rounds': 2,       # Extra rounds in naïve hybrid (assumed; swept 0–4 in Exp 9)
'naive_combiner_penalty_ms': (0.25, 0.7),  # Naïve hybrid non-adaptive coordination penalty

# QKD resource pool
'qkd_generation_rate_kbps': 96.0,
'qkd_pool_capacity_bits': 60000,
'qkd_key_bits_per_session': 1024,
'qkd_availability': 0.85,
'qkd_max_wait_ms': 18.0,       # Max wait for pool refill (naïve hybrid and QKD-only)
'qkd_initial_fill_ratio': 0.65,

# Traffic (M/M/1 queue)
'service_rate': 18.0,           # Sessions/s
'baseline_arrival_rate': 6,     # Sessions/s (baseline)
'arrival_rates': [4, 6, 8, 10, 12, 14, 16],  # B.1: rho < 1 (mu = 18)
```

To modify parameters, edit `config.py` directly. All experiments read parameters from `CONFIG` at runtime.

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/meetabdulalim/Migration-Aware-Hybrid-Cryptographic-Framework-Network-Simulation.git
cd Migration-Aware-Hybrid-Cryptographic-Framework-Network-Simulation
```

### Requirements

- Python **3.9 or higher**
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install numpy matplotlib networkx
```

### Verify Installation

```bash
python -c "import numpy, matplotlib, networkx; print('All dependencies installed.')"
```

---

## Contributing

Contributions, forks, and pull requests are welcome. If you'd like to use, extend, or modify this simulation code, please follow these guidelines:

1. **Fork the repository** and create a new branch for your change (e.g., `feature/new-experiment`, `fix/qkd-pool-bug`).
2. **Keep reproducibility intact** — do not change the default `seed=42` or the statistical setup (120 runs × 300 sessions) in `config.py` unless your PR is specifically about extending the experimental design. If you do change it, clearly document the new configuration and update `results/raw/` and `results/plots/` accordingly.
3. **Match the existing code structure** — new experiments go under `experiments/`, new shared logic under `core/`, and new simulation building blocks under `models/`. Keep one file per experiment, following the `expN_*.py` naming convention.
4. **Test before submitting** — run `python main.py` (or the specific experiment you touched) and confirm it completes without errors and produces sensible CSV/plot outputs.
5. **Document your changes** — update this README (Project Structure, Output Files, etc.) if you add new files, parameters, or experiments.
6. **Describe your PR clearly** — explain what changed, why, and which paper claim or research question it relates to (if any).
7. **Cite the paper** if your fork or derivative work builds on this framework (see [Citation](#citation)).

For bug reports or feature requests, please open an Issue describing the problem, steps to reproduce (if applicable), and your environment (Python version, OS).

---

## Usage

### Run All Experiments

```bash
python main.py
```

This runs all 10 experiments sequentially and saves outputs to:
- `results/raw/` — CSV files with all numerical results
- `results/plots/` — PNG figures corresponding to Figs. 4–12 in the paper; Table 5 comes from `results/raw/exp9_naive_sensitivity.csv`


### Run Individual Experiments

Each experiment can be run independently:

```bash
# Experiment 1 — Baseline latency comparison (Fig. 4)
python -c "from experiments.exp1_mode_comparison import run_exp1; run_exp1()"

# Experiment 2 — Scalability under increasing network size (Fig. 5)
python -c "from experiments.exp2_scalability import run_exp2; run_exp2()"

# Experiment 3 — Multi-hop impact (Fig. 6)
python -c "from experiments.exp3_hop_impact import run_exp3; run_exp3()"

# Experiment 4 — QKD entropy utilization (Fig. 8)
python -c "from experiments.exp4_qkd_utilization import run_exp4; run_exp4()"

# Experiment 5 — Overhead breakdown (Fig. 7)
python -c "from experiments.exp5_overhead_breakdown import run_exp5; run_exp5()"

# Experiment 6 — Migration-aware performance (Fig. 9)
python -c "from experiments.exp6_migration_aware import run_exp6; run_exp6()"

# Experiment 7 — Adaptive fallback under QKD outage (Fig. 10)
python -c "from experiments.exp7_adaptive_fallback import run_exp7; run_exp7()"

# Experiment 8 — secret-key sessions under partial compromise (Fig. 11)
python -c "from experiments.exp8_partial_compromise import run_exp8; run_exp8()"

# Experiment 9 — Naïve-hybrid extra-rounds sensitivity (Table 5)
python -c "from experiments.exp9_naive_sensitivity import run_exp9; run_exp9()"

# Experiment 10 — QKD availability x link-coverage sweep (Fig. 12)
python -c "from experiments.exp10_availability_sweep import run_exp10; run_exp10()"
```

Alternatively, comment out unwanted experiments in `main.py` and run `python main.py`.

---

## Results

Pre-computed results from the paper run are included in `results/raw/` and `results/plots/`. Running `main.py` will overwrite them with freshly computed results. Due to the fixed seed (`seed=42`), all numerical results are reproducible and match the paper.

### Experiment 1: Baseline Latency Comparison

*Session establishment latency across five cryptographic schemes at the baseline configuration. Source: `results/raw/exp1_mode_comparison.csv`*

| Scheme | Mean Latency (ms) | 95% CI | Session Success Rate |
|--------|:-----------------:|:------:|:--------------------:|
| Classical | 17.30 | ±0.01 | 100% |
| PQC | 18.54 | ±0.01 | 100% |
| QKD-only | 19.64 | ±0.02 | **46.6%** |
| **Proposed Hybrid** | **29.73** | **±0.05** | **100%** |
| Naïve Hybrid (no fallback) | 39.85 | ±0.03 | 46.5% |

Latencies of QKD-only and the naïve hybrid are over established sessions only. The proposed hybrid incurs ~11.19 ms additional overhead over PQC-only, while completely removing the 53.4% session failure rate of QKD-only operation.

### Experiment 5: Overhead Breakdown

*Per-component mean contribution to proposed hybrid session latency. Source: `results/raw/exp5_overhead_breakdown.csv`*

| Protocol Component | Mean Latency (ms) |
|--------------------|:-----------------:|
| Classical Key Exchange (ECDHE + control) | 6.75 |
| PQC Key Exchange (ML-KEM-768) | **8.00** |
| QKD Entropy Retrieval (averaged over sessions) | 3.87 |
| Hybrid KDF (modeled delay) | **0.30** |

This experiment samples the path length from the topology (Fig. 7), so its total differs slightly from Exp 1, which uses 3 fixed hops. The KDF/combiner logic contributes only 0.30 ms. The overhead originates from the individual key establishment protocols, not the hybrid composition itself.

### Experiment 6: Migration-Aware Performance

*Session success rate and key-source coverage across three deployment phases. Source: `results/raw/exp6_migration_aware.csv`*

| Deployment Phase | Session Success Rate | Key-Source Coverage |
|-----------------|:--------------------:|:----:|
| Baseline Hybrid (Classical+PQC) | 100% | 0.667 |
| Partial/Intermittent QKD | 100% | 0.739 |
| QKD-Enhanced Hybrid | 100% | 0.821 |

100% session continuity is maintained across all migration phases. Key-source coverage increases as QKD infrastructure expands. The scenarios use QKD availability 0 / 0.40 / 0.85 with per-link coverage 0.82 (3 hops).

### Experiment 8: Secret-Key Sessions Under Partial Compromise

*Fraction of sessions with a secret key, per compromised-source set B. A session counts if a key was established (simulator) and at least one contributing source lies outside B (Lemma 1). Source: `results/raw/exp8_partial_compromise.csv`*

| Compromised set B | Classical | PQC | QKD-only | Naïve Hybrid | Proposed Hybrid |
|---|:-:|:-:|:-:|:-:|:-:|
| None | 1.000 | 1.000 | 0.438 | 0.436 | 1.000 |
| Classical | 0 | 1.000 | 0.438 | 0.436 | 1.000 |
| PQC | 1.000 | 0 | 0.438 | 0.436 | 1.000 |
| QKD | 1.000 | 1.000 | 0 | 0.436 | 1.000 |
| Classical + PQC | 0 | 0 | 0.438 | 0.436 | **0.440** |
| Classical + QKD | 0 | 1.000 | 0 | 0.436 | 1.000 |
| PQC + QKD | 1.000 | 0 | 0 | 0.436 | 1.000 |
| All three | 0 | 0 | 0 | 0 | 0 |

Which sources contribute and whether a key is established come from the simulator; the compromise set B is a scenario assumption. The naïve hybrid uses the same combiner but has no fallback, so it yields a key in only ~44% of sessions. QKD-only and the naïve hybrid are bounded by QKD availability (~44%) because neither has a fallback, so their bars change only when the sources they use are broken (QKD for QKD-only; all three sources for the naïve hybrid). When classical and PQC are both broken, the proposed hybrid's fallback sessions (Mode 0, ~56%) are exposed; high-assurance deployments should use a fail-closed policy (`require_qkd`), under which these sessions abort instead of being exposed.

---

## Output Files

After running `main.py`, the following files are generated:

| File | Content | Paper Figure |
|------|---------|:------------:|
| `results/raw/exp1_mode_comparison.csv` | Mean latency, CI, success rate per mode | Fig. 4 |
| `results/raw/exp2_scalability.csv` | Latency vs. endpoint count per mode | Fig. 5 |
| `results/raw/exp3_hop_impact.csv` | Latency vs. hop count per mode | Fig. 6 |
| `results/raw/exp4_qkd_utilization.csv` | QKD consumption vs. network size and generation rate | Fig. 8 |
| `results/raw/exp5_overhead_breakdown.csv` | Per-component mean delay | Fig. 7 |
| `results/raw/exp6_migration_aware.csv` | Success rate and key-source coverage per migration phase | Fig. 9 |
| `results/raw/exp7_adaptive_fallback_timeline.csv` | Per-batch success rate and key-source coverage (26 batches, outage = batches 10-16; 120 runs x 300 sessions per batch) with 95% CI | Fig. 10 |
| `results/raw/exp8_partial_compromise.csv` | Secret-key session fraction per scheme per compromise scenario | Fig. 11 |
| `results/raw/exp9_naive_sensitivity.csv` | Naïve-hybrid sensitivity to the assumed number of extra control rounds | Table 5 |
| `results/raw/exp10_availability_sweep.csv` | Success, key-source coverage, latency vs QKD availability x link coverage | Fig. 12 |
| `results/plots/exp1_mode_comparison_latency.png` | Bar chart — baseline latency | Fig. 4 |
| `results/plots/exp2_scalability_all_schemes.png` | Line chart — latency vs. endpoints | Fig. 5 |
| `results/plots/exp3_hop_impact_all_schemes.png` | Line chart — latency vs. hops | Fig. 6 |
| `results/plots/exp4_qkd_utilization.png` | Three-panel chart — QKD consumption and scarcity | Fig. 8 |
| `results/plots/exp5_overhead_breakdown.png` | Bar chart — component breakdown | Fig. 7 |
| `results/plots/exp6_migration_aware.png` | Grouped bar — migration phases | Fig. 9 |
| `results/plots/exp7_adaptive_fallback_timeline.png` | Timeline — fallback behavior (injected outage) | Fig. 10 |
| `results/plots/exp8_partial_compromise.png` | Grouped bar — secret-key sessions under compromise | Fig. 11 |
| `results/plots/exp10_availability_sweep.png` | Success / key-source coverage vs QKD availability and link coverage | Fig. 12 |

---

## Reproducibility

All results in the paper are fully reproducible. The simulation uses a global random seed (`seed=42` in `config.py`), set at startup via:

```python
from core.utils import set_seed
set_seed(CONFIG['seed'])
```

Running `python main.py` with the default configuration will produce numerical results identical to those reported in the paper's Section 6 and the pre-computed files in `results/raw/`.

**Statistical setup:**
- 120 independent runs per configuration
- 300 sessions per run (every experiment; Exp 7: per batch). 95% CIs are taken over the 120 per-run means
- 95% confidence intervals: `CI = 1.96 × σ / √n`
- All figures generated directly from CSV files

---

## Design Decisions & Validity

### Why stochastic delays rather than a hardware testbed?

This simulation targets **architecture-level evaluation**, not implementation benchmarking. The goal is to compare the structural behavior of five cryptographic composition strategies under realistic network and resource conditions — not to measure the performance of a specific cryptographic library or QKD vendor.

Stochastic delay ranges are based on published benchmarks for ML-KEM-768 (Kyber-768), ECDHE, and HKDF, as end-to-end phase latencies for an edge-gateway-class device. This approach:
1. Isolates architectural differences from implementation-specific optimizations
2. Produces statistically robust comparisons via 120 independent runs
3. Avoids platform-specific or vendor-specific bias
4. Enables systematic parameter sweeps not feasible on hardware testbeds

Experimental validation using physical QKD testbeds and hardware-implemented PQC primitives is identified as an important direction for future work.

### Connection to paper claims

Every numerical claim in Section 6 (Performance Evaluation) of the paper traces directly to a specific CSV file in `results/raw/`. The figures in `results/plots/` correspond to Figures 4–12 in the paper (Fig. 7 is regenerated with the same data; only font rendering may differ).

---

## Citation

If you use this simulation code or build upon the proposed framework in your research, please cite:

<!-- ```bibtex
@article{alim2025migration,
  title   = {A Migration-Aware Hybrid Cryptographic Framework With Adaptive
             Fallback for Classical, Post-Quantum, and Quantum Key
             Distribution Security},
  author  = {[Author Name(s)]},
  journal = {Computer Networks},
  year    = {2026},
  doi     = {[to be added]}
}
``` -->

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## Acknowledgements

Network topology generation uses the [NetworkX](https://networkx.org/) library.
Numerical computation uses [NumPy](https://numpy.org/).
Figures are generated with [Matplotlib](https://matplotlib.org/).
