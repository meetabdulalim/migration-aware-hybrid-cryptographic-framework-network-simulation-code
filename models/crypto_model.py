import random
from config import CONFIG


def classical_crypto_delay_ms():
    return random.uniform(*CONFIG['classical_crypto_ms'])


def pqc_delay_ms():
    return random.uniform(*CONFIG['pqc_delay_ms'])


def kdf_delay_ms():
    return random.uniform(*CONFIG['kdf_delay_ms'])


def classical_round_trip_ms():
    return random.uniform(*CONFIG['classical_round_trip_ms'])


def control_processing_ms():
    return random.uniform(*CONFIG['control_processing_ms'])


def qkd_auth_processing_ms():
    return random.uniform(*CONFIG['qkd_auth_processing_ms'])


def naive_combiner_penalty_ms():
    return random.uniform(*CONFIG['naive_combiner_penalty_ms'])
