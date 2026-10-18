from models.crypto_model import (
    classical_crypto_delay_ms,
    pqc_delay_ms,
    kdf_delay_ms,
    classical_round_trip_ms,
    control_processing_ms,
    qkd_auth_processing_ms,
    naive_combiner_penalty_ms,
)
from models.network_model import sample_route_hops, hop_propagation_delay_ms, qkd_path_available
from models.qkd_model import QKDResourcePool
from models.traffic_model import queue_delay_ms
from config import CONFIG


NO_FALLBACK_MODES = ('qkd', 'hybrid_no_fallback', 'naive_hybrid')


def _mode_flags(mode):
    return {
        'use_classical': mode in ['classical', 'hybrid', 'naive_hybrid', 'hybrid_no_qkd', 'hybrid_no_fallback'],
        'use_pqc': mode in ['pqc', 'hybrid', 'naive_hybrid', 'hybrid_no_qkd', 'hybrid_no_fallback'],
        'use_qkd': mode in ['qkd', 'hybrid', 'naive_hybrid', 'hybrid_no_fallback'],
        'use_kdf': mode in ['qkd', 'hybrid', 'naive_hybrid', 'hybrid_no_qkd', 'hybrid_no_fallback'],
    }


def _source_coverage(mode, qkd_used=False, established=True):
    """A.5: measured, constant-free replacement for the old resilience score:
    share of the three key sources (classical, PQC, QKD) that actually
    contributed to the session key (0 if no key was established)."""
    if not established:
        return 0.0
    f = _mode_flags(mode)
    return (int(f['use_classical']) + int(f['use_pqc']) + int(qkd_used)) / 3.0


def simulate_session(
    hops=None,
    num_endpoints=None,
    mode='hybrid',
    fallback=True,
    qkd_prob=None,
    arrival_rate=None,
    qkd_pool=None,
    force_qkd_success=None,
    force_qkd_failure=None,
):

    
    num_endpoints = num_endpoints if num_endpoints is not None else CONFIG['baseline_endpoints']
    hops = hops if hops is not None else sample_route_hops(num_endpoints)
    arrival_rate = arrival_rate if arrival_rate is not None else CONFIG['baseline_arrival_rate']
    qkd_pool = qkd_pool if qkd_pool is not None else QKDResourcePool(availability=qkd_prob)
    flags = _mode_flags(mode)

    network_ms = hop_propagation_delay_ms(hops)
    queue_ms = queue_delay_ms(arrival_rate)

    classical_ms = 0.0
    pqc_ms = 0.0
    qkd_coord_ms = 0.0
    qkd_wait_ms = 0.0
    kdf_ms = 0.0
    qkd_used = False
    fallback_used = False
    failure_reason = ''
    qkd_generated_bits = 0.0
    qkd_consumed_bits = 0

    if flags['use_classical']:
        classical_ms = (
            CONFIG['classical_rounds'] * classical_round_trip_ms()
            + control_processing_ms()
            + classical_crypto_delay_ms()
        )

    if flags['use_pqc']:
        pqc_ms = pqc_delay_ms()

    if flags['use_qkd']:
        inter_arrival_ms = 1000.0 / max(arrival_rate, 1e-9)
        qkd_pool.replenish(inter_arrival_ms)

        # -------------------------------------------------
        # Controlled hooks for experiment-level validation
        # -------------------------------------------------
        if force_qkd_success is True:
            qkd_used = True
            qkd_wait_ms = 0.0
            qkd_generated_bits = CONFIG['qkd_key_bits_per_session']
            qkd_consumed_bits = CONFIG['qkd_key_bits_per_session']
            qkd_coord_ms = (
                CONFIG['qkd_control_rounds'] * classical_round_trip_ms()
                + qkd_auth_processing_ms()
            )
            if mode == 'naive_hybrid':
                qkd_coord_ms += CONFIG['naive_extra_rounds'] * classical_round_trip_ms()

        elif force_qkd_failure is True:
            failure_reason = 'forced_qkd_unavailable'
            if mode in NO_FALLBACK_MODES or not fallback:
                return {
                    'latency_ms': None,
                    'classical_ms': classical_ms,
                    'pqc_ms': pqc_ms,
                    'qkd_ms': 0.0,
                    'qkd_wait_ms': 0.0,
                    'kdf_ms': 0.0,
                    'network_ms': network_ms,
                    'queue_ms': queue_ms,
                    'route_hops': hops,
                    'qkd_used': False,
                    'fallback_used': False,
                    'success': False,
                    'failure_reason': failure_reason,
                    'qkd_consumed_bits': 0,
                    'qkd_generated_bits': 0.0,
                    'key_source_coverage': 0.0,
                }
            fallback_used = flags['use_qkd']

        else:
            path_has_qkd = qkd_path_available(hops)
            allow_wait = mode in ['qkd', 'naive_hybrid', 'hybrid_no_fallback']
            qkd_result = qkd_pool.try_acquire(
                key_bits=CONFIG['qkd_key_bits_per_session'],
                qkd_path_available=path_has_qkd,
                qkd_prob=qkd_prob,
                allow_wait=allow_wait,
            )
            if qkd_result.used:
                qkd_used = True
                qkd_wait_ms = qkd_result.wait_ms
                qkd_generated_bits = qkd_result.generated_bits
                qkd_consumed_bits = qkd_result.consumed_bits
                qkd_coord_ms = (
                    CONFIG['qkd_control_rounds'] * classical_round_trip_ms()
                    + qkd_auth_processing_ms()
                )
                if mode == 'naive_hybrid':
                    qkd_coord_ms += CONFIG['naive_extra_rounds'] * classical_round_trip_ms()
            else:
                failure_reason = qkd_result.reason
                if mode in NO_FALLBACK_MODES or not fallback:
                    return {
                        'latency_ms': None,
                        'classical_ms': classical_ms,
                        'pqc_ms': pqc_ms,
                        'qkd_ms': 0.0,
                        'qkd_wait_ms': qkd_wait_ms,
                        'kdf_ms': 0.0,
                        'network_ms': network_ms,
                        'queue_ms': queue_ms,
                        'route_hops': hops,
                        'qkd_used': False,
                        'fallback_used': False,
                        'success': False,
                        'failure_reason': failure_reason,
                        'qkd_consumed_bits': 0,
                        'qkd_generated_bits': qkd_generated_bits,
                        'key_source_coverage': 0.0,
                    }
                fallback_used = flags['use_qkd']

    if flags['use_kdf']:
        kdf_ms = kdf_delay_ms()
        if mode == 'naive_hybrid':
            kdf_ms += naive_combiner_penalty_ms()

    total = classical_ms + pqc_ms + qkd_coord_ms + qkd_wait_ms + kdf_ms + network_ms + queue_ms
    return {
        'latency_ms': total,
        'classical_ms': classical_ms,
        'pqc_ms': pqc_ms,
        'qkd_ms': qkd_coord_ms,
        'qkd_wait_ms': qkd_wait_ms,
        'kdf_ms': kdf_ms,
        'network_ms': network_ms,
        'queue_ms': queue_ms,
        'route_hops': hops,
        'qkd_used': qkd_used,
        'fallback_used': fallback_used,
        'success': True,
        'failure_reason': failure_reason,
        'qkd_consumed_bits': qkd_consumed_bits,
        'qkd_generated_bits': qkd_generated_bits,
        'key_source_coverage': _source_coverage(mode, qkd_used=qkd_used),
    }