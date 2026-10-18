import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_RAW = os.path.join(BASE_DIR, 'results', 'raw')
RESULTS_PLOTS = os.path.join(BASE_DIR, 'results', 'plots')

os.makedirs(RESULTS_RAW, exist_ok=True)
os.makedirs(RESULTS_PLOTS, exist_ok=True)

CONFIG = {
    'seed': 42,
    'num_runs': 120,
    'sessions_per_setting': 300,
    'baseline_endpoints': 60,
    'baseline_arrival_rate': 6,
    'baseline_hops': 3,

    'endpoints_list': [20, 40, 60, 80, 100],
    'hop_counts': [1, 2, 3, 4, 5],
    'arrival_rates': [4, 6, 8, 10, 12, 14, 16],
    'qkd_availability_sweep': [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    'qkd_coverage_sweep': [0.6, 0.82, 0.95],

    # Migration stages: classical+PQC -> partial/intermittent QKD -> QKD-enhanced
    'migration_stages': [0, 1, 2],

    # Schemes required by paper
    'paper_modes': ['classical', 'pqc', 'qkd', 'hybrid', 'naive_hybrid'],

    # Network model (architecture-level plausible ranges)
    'avg_degree': 4,
    'rewire_prob': 0.25,
    'per_hop_delay_ms': (0.8, 1.6),
    'qkd_link_coverage': 0.82,

    # Control-plane delay model (ms)
    'classical_round_trip_ms': (1.8, 3.2),
    'control_processing_ms': (0.3, 0.9),
    'qkd_auth_processing_ms': (0.8, 1.8),
    'classical_rounds': 2,
    'qkd_control_rounds': 3,
    'naive_extra_rounds': 2, 
    'naive_extra_rounds_sweep': [0, 1, 2, 3, 4],

    # Cryptographic compute delay (ms)
    'classical_crypto_ms': (0.8, 1.5),
    'pqc_delay_ms': (6.0, 10.0),
    'kdf_delay_ms': (0.1, 0.5),
    'naive_combiner_penalty_ms': (0.25, 0.7),

    # QKD resource model
    'qkd_generation_rate_kbps': 96.0,
    'qkd_scarcity_rates_kbps': [1, 2, 3, 4, 6, 12, 24, 48, 96],
    'qkd_pool_capacity_bits': 60000,
    'qkd_initial_fill_ratio': 0.65,
    'qkd_key_bits_per_session': 1024,
    'qkd_availability': 0.85,
    'qkd_max_wait_ms': 18.0,

    # Queue / service model
    'service_rate': 18.0,
    'congestion_cap_ms': 60.0,
}
